import requests
import os
import urllib.parse
import threading
from itertools import islice
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor
from Start_up.remove_file import delete_empty_text_files
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from colorama import Fore, Style, init
import multiprocessing

init(autoreset=True)

MAX_WORKERS = min(10, multiprocessing.cpu_count() * 2)  # Reduce worker threads to prevent memory exhaustion

redirect_params = {
    "redirect", "url", "next", "return", "r", "u", "goto", "target",
    "forward", "continue", "checkout_url", "dest", "destination", "go",
    "image_url", "redir", "redirect_uri", "redirect_url", "return_path",
    "return_to", "returnTo", "rurl", "view"
}

redirect_paths = {
    "/redirect/", "/go/", "/continue/", "/checkout/", "/out/", "/exit/",
    "/track/", "/trackback/", "/leave/", "/away/", "/visit/", "/r/",
    "/", "/cgi-bin/redirect.cgi?", "/out?", "/login?to="
}

log_queue = Queue(maxsize=1000)  # Prevent unbounded memory usage in logging

def read_urls_in_batches(filename, batch_size=10):
    """Generator to read a file in batches of 10 URLs at a time"""
    try:
        with open(filename, 'r') as file:
            while True:
                batch = list(islice(file, batch_size))  # Read next 10 URLs
                if not batch:
                    break
                yield [url.strip() for url in batch]  # Yield cleaned URLs
    except FileNotFoundError:
        print(f"{Fore.RED}[-] Input file {filename} not found!{Style.RESET_ALL}")
        return

def inject_query(url, param, payload):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    query_params[param] = payload  # Inject payload
    new_query = urlencode(query_params, doseq=True)
    return urlunparse(parsed_url._replace(query=new_query))

# Initialize a session to reuse TCP connections
session = requests.Session()

def log_writer(log_file_path):
    """ Writes logs asynchronously to avoid memory buildup. """
    with open(log_file_path, 'a',encoding='utf-8') as log_file:
        while True:
            try:
                message = log_queue.get(timeout=2)
                if message is None:
                    break  
                log_file.write(message + "\n")
                log_file.flush()  # Flush data to disk periodically
                print(message)
            except Empty:
                continue  

def filter_urls(urls):
    """ Filters URLs containing redirection parameters or paths. """
    return [
        url for url in urls
        if any(param in urllib.parse.parse_qs(urllib.parse.urlparse(url).query) for param in redirect_params)
        or any(path in urllib.parse.urlparse(url).path for path in redirect_paths)
    ]

def test_redirect(url, payload):
    """ Tests for open redirect vulnerabilities in a URL. """
    try:
        parsed_url = urllib.parse.urlparse(url)
        original_domain = parsed_url.netloc  # Extract domain of the input URL
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        # Test query-based injection
        for param in query_params:
            if param in redirect_params:
                injected_url = inject_query(url, param, payload)
                try:
                    response = session.get(injected_url, allow_redirects=False, timeout=(5, 10))
                    
                    if response.status_code in [301, 302, 303, 307, 308] and 'Location' in response.headers:
                        redirected_url = response.headers['Location']
                        redirected_domain = urllib.parse.urlparse(redirected_url).netloc

                        if redirected_domain and redirected_domain != original_domain:
                            log_queue.put(f"{Fore.GREEN}[TRUE POSITIVE] {injected_url} -> {response.status_code} Redirects to: {redirected_url}")
                        else:
                            log_queue.put(f"{Fore.YELLOW}[FALSE POSITIVE] {injected_url} -> Redirected to same domain: {redirected_url}")
                    else:
                        log_queue.put(f"{Fore.YELLOW}[QUERY] {injected_url} -> {response.status_code} No Redirect Detected")
                except requests.RequestException as req_err:
                    log_queue.put(f"{Fore.RED}[ERROR] {injected_url}: {str(req_err)}")

        # Test path-based injection
        for path in redirect_paths:
            if path in url:
                injected_url = f"{url.rstrip('/')}/{urllib.parse.quote_plus(payload)}"
                try:
                    response = session.get(injected_url, allow_redirects=False, timeout=(5, 10))
                    
                    if response.status_code in [301, 302, 303, 307, 308] and 'Location' in response.headers:
                        redirected_url = response.headers['Location']
                        redirected_domain = urllib.parse.urlparse(redirected_url).netloc

                        if redirected_domain and redirected_domain != original_domain:
                            log_queue.put(f"{Fore.GREEN}[TRUE POSITIVE] {injected_url} -> {response.status_code} Redirects to: {redirected_url}")
                        else:
                            log_queue.put(f"{Fore.YELLOW}[FALSE POSITIVE] {injected_url} -> Redirected to same domain: {redirected_url}")
                    else:
                        log_queue.put(f"{Fore.YELLOW}[PATH] {injected_url} -> {response.status_code} No Redirect Detected")
                except requests.RequestException as req_err:
                    log_queue.put(f"{Fore.RED}[ERROR] {injected_url}: {str(req_err)}")
    except Exception as e:
        log_queue.put(f"{Fore.RED}[ERROR] {url}: {str(e)}")


def scan_urls(bug_path, urls, payloads):
    """ Uses a thread pool to scan URLs in batches. """
    log_file_path = f'{bug_path}/LOGS.txt'
    
    log_thread = threading.Thread(target=log_writer, args=(log_file_path,))
    log_thread.start()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            for url in urls:
                for payload in payloads:
                    executor.submit(test_redirect, url, payload)

    log_queue.put(None)  
    log_thread.join()  

def open_redirect(bug_path, target):
    """ Main function to execute the scan. """
    input_file = f"{bug_path}/URL_FOR_{target}.txt"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "payloads.txt")
    
    for urls in read_urls_in_batches(input_file,10):
            filtered_urls = filter_urls(urls)
            if filtered_urls:
                print(f"{Fore.BLUE}Filtered {len(filtered_urls)} potential redirect URLs from {len(urls)} total URLs.")
                for payloads in read_urls_in_batches(file_path,10):
                        scan_urls(bug_path, filtered_urls, payloads)  
    delete_empty_text_files(bug_path)
