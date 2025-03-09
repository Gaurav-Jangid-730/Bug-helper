import requests
import os
import urllib.parse
import threading
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
from Start_up.remove_file import delete_empty_text_files
from colorama import Fore, Style, init

init(autoreset=True)

TIMEOUT = 10  # Reduced timeout to avoid hanging requests
MAX_WORKERS = 10  # Limit thread usage to avoid high CPU/memory consumption
MAX_URLS = 100  # Limit the number of URLs to process
MAX_PAYLOADS = 10  # Limit payloads per URL to prevent excessive testing

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

# Logging queue to avoid excessive memory usage
log_queue = Queue()

# Function to write logs asynchronously
def log_writer(log_file_path):
    with open(log_file_path, 'a') as log_file:
        while True:
            message = log_queue.get()
            if message is None:
                break  # Exit logging thread
            log_file.write(message + "\n")

# Function to filter URLs containing redirection parameters or paths
def filter_urls(urls):
    filtered = []
    for url in urls[:MAX_URLS]:  # Limit processing to MAX_URLS
        parsed_url = urllib.parse.urlparse(url)
        
        # Check if query parameters match known redirect parameters
        query_params = urllib.parse.parse_qs(parsed_url.query)
        if any(param in query_params for param in redirect_params):
            filtered.append(url)
            continue
        
        # Check if URL path matches known redirect paths
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
                    log_message = f"[QUERY] {injected_url} -> {response.status_code}"
                    print(Fore.GREEN + log_message)
                    log_queue.put(log_message)
                except requests.RequestException as req_err:
                    error_message = f"[ERROR] {injected_url}: {str(req_err)}"
                    print(Fore.RED + error_message)
                    log_queue.put(error_message)

        # Test path-based injection
        for path in redirect_paths:
            if path in url:
                injected_url = f"{url.rstrip('/')}/{urllib.parse.quote_plus(payload)}"
                try:
                    response = requests.get(injected_url, allow_redirects=False, timeout=TIMEOUT)
                    log_message = f"[PATH] {injected_url} -> {response.status_code}"
                    print(Fore.GREEN + log_message)
                    log_queue.put(log_message)
                except requests.RequestException as req_err:
                    error_message = f"[ERROR] {injected_url}: {str(req_err)}"
                    print(Fore.RED + error_message)
                    log_queue.put(error_message)
    except Exception as e:
        error_message = f"[ERROR] {url}: {str(e)}"
        print(Fore.RED + error_message)
        log_queue.put(error_message)

# Function to start scanning using a thread pool
def scan_urls(bug_path, urls, payloads):
    log_file_path = f'{bug_path}/LOGS.txt'
    
    # Start log writing in a separate thread
    log_thread = threading.Thread(target=log_writer, args=(log_file_path,))
    log_thread.start()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for url in urls:
            for payload in payloads[:MAX_PAYLOADS]:  # Limit payloads per URL
                executor.submit(test_redirect, url, payload)

    log_queue.put(None)  # Signal log writer to stop
    log_thread.join()  # Wait for log writing to finish

# Main function
def open_redirect(bug_path, target):
    input_file = f"{bug_path}/URL_FOR_{target}.txt"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "payloads.txt")
    
    # Read URLs and payloads from files
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

    # Filter relevant URLs
    filtered_urls = filter_urls(urls)
    print(f"{Fore.BLUE}Filtered {len(filtered_urls)} potential redirect URLs from {len(urls)} total URLs.")

    # Scan for open redirects
    scan_urls(bug_path, filtered_urls, payloads)
    delete_empty_text_files(bug_path)
