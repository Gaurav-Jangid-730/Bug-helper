import requests
import os
import urllib.parse
import threading
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor
from Start_up.remove_file import delete_empty_text_files
from colorama import Fore, Style, init

init(autoreset=True)

TIMEOUT = 10  
MAX_WORKERS = 10
MAX_PAYLOADS = 10  
MAX_URLS = 10

# Common redirect parameters
redirect_params = {
    "redirect", "url", "next", "return", "r", "u", "goto", "target",
    "forward", "continue", "checkout_url", "dest", "destination", "go",
    "image_url", "redir", "redirect_uri", "redirect_url", "return_path",
    "return_to", "returnTo", "rurl", "view"
}

# Common redirect paths
redirect_paths = {
    "/redirect/", "/go/", "/continue/", "/checkout/", "/out/", "/exit/",
    "/track/", "/trackback/", "/leave/", "/away/", "/visit/", "/r/",
    "/", "/cgi-bin/redirect.cgi?", "/out?", "/login?to="
}

log_queue = Queue()

# Function to write logs asynchronously
def log_writer(log_file_path):
    with open(log_file_path, 'a') as log_file:
        while True:
            try:
                message = log_queue.get(timeout=2)
                if message is None:
                    break  
                log_file.write(message + "\n")
                print(message)  
            except Empty:
                continue  

# Function to filter URLs containing redirection parameters or paths
def filter_urls(urls):
    filtered = []
    for url in urls:  
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        # Check query params
        if any(param in query_params for param in redirect_params):
            filtered.append(url)
            continue
        
        # Check path
        if any(path in parsed_url.path for path in redirect_paths):
            filtered.append(url)

    return filtered

# Function to test URL with a given payload
def test_redirect(url, payload):
    try:
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        # Test query-based injection
        for param in query_params:
            if param in redirect_params:
                injected_url = f"{url}&{param}={urllib.parse.quote_plus(payload)}"
                try:
                    response = requests.get(injected_url, allow_redirects=False, timeout=TIMEOUT)
                    if response.status_code in [301, 302, 303, 307, 308] and 'Location' in response.headers:
                        log_queue.put(f"{Fore.GREEN}[QUERY] {injected_url} -> {response.status_code} Redirects to: {response.headers['Location']}")
                    else:
                        log_queue.put(f"{Fore.YELLOW}[QUERY] {injected_url} -> {response.status_code} No Redirect Detected")
                except requests.RequestException as req_err:
                    log_queue.put(f"{Fore.RED}[ERROR] {injected_url}: {str(req_err)}")

        # Test path-based injection
        for path in redirect_paths:
            if path in url:
                injected_url = f"{url.rstrip('/')}/{urllib.parse.quote_plus(payload)}"
                try:
                    response = requests.get(injected_url, allow_redirects=False, timeout=TIMEOUT)
                    if response.status_code in [301, 302, 303, 307, 308] and 'Location' in response.headers:
                        log_queue.put(f"{Fore.GREEN}[PATH] {injected_url} -> {response.status_code} Redirects to: {response.headers['Location']}")
                    else:
                        log_queue.put(f"{Fore.YELLOW}[PATH] {injected_url} -> {response.status_code} No Redirect Detected")
                except requests.RequestException as req_err:
                    log_queue.put(f"{Fore.RED}[ERROR] {injected_url}: {str(req_err)}")
    except Exception as e:
        log_queue.put(f"{Fore.RED}[ERROR] {url}: {str(e)}")

# Function to start scanning using a thread pool
def scan_urls(bug_path, urls, payloads):
    log_file_path = f'{bug_path}/LOGS.txt'
    
    log_thread = threading.Thread(target=log_writer, args=(log_file_path,))
    log_thread.start()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for x in range(0,len(urls), MAX_URLS):
            url_batch = urls[x : x + MAX_URLS]
            for url in url_batch:
                for i in range(0, len(payloads), MAX_PAYLOADS):  # Process all payloads in batches of MAX_PAYLOADS
                    batch = payloads[i : i + MAX_PAYLOADS]
                    for payload in batch:
                        executor.submit(test_redirect, url, payload)

    log_queue.put(None)  # Signal log writer to stop
    log_thread.join()  # Wait for log writing to finish

# Main function
def open_redirect(bug_path, target):
    input_file = f"{bug_path}/URL_FOR_{target}.txt"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "payloads.txt")
    
    try:
        with open(input_file, "r") as f:
            urls = [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        print(f"{Fore.RED}[-] Input file {input_file} not found!{Style.RESET_ALL}")
        return
    
    try:
        with open(file_path, "r") as f:
            payloads = [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        print(f"{Fore.RED}[-] Payloads file at path {file_path} is not found!{Style.RESET_ALL}")
        return

    filtered_urls = filter_urls(urls)
    print(f"{Fore.BLUE}Filtered {len(filtered_urls)} potential redirect URLs from {len(urls)} total URLs.")

    scan_urls(bug_path, filtered_urls, payloads)
    delete_empty_text_files(bug_path)
