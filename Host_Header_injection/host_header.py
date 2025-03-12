import requests
import threading
from itertools import islice
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse
from colorama import Fore, Style, init
import multiprocessing

init(autoreset=True)

MAX_WORKERS = min(10, multiprocessing.cpu_count() * 2)  # Control thread usage
log_queue = Queue(maxsize=1000)  # Prevent unbounded memory usage in logging

# Initialize session for efficiency
session = requests.Session()

def read_urls_in_batches(filename, batch_size=10):
    """Reads URLs from a file in batches"""
    try:
        with open(filename, 'r') as file:
            while True:
                batch = list(islice(file, batch_size))
                if not batch:
                    break
                yield [url.strip() for url in batch]
    except FileNotFoundError:
        print(f"{Fore.RED}[-] Input file {filename} not found!{Style.RESET_ALL}")
        return

def log_writer(log_file_path):
    """Writes logs asynchronously to avoid memory buildup."""
    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        while True:
            try:
                message = log_queue.get(timeout=2)
                if message is None:
                    break  # Stop logging
                log_file.write(message + "\n")
                log_file.flush()
                print(message)
            except Empty:
                continue

def test_host_header(url):
    """Tests different Host Header injection techniques."""
    try:
        parsed_url = urlparse(url)
        original_host = parsed_url.netloc
        headers_list = [
            {"Host": "evil.com"},
            {"Host": original_host, "X-Forwarded-Host": "evil.com"},
            {"Host": f"evil.com: {original_host}"},
            {"Host": f"test-{original_host}"}
        ]
        
        for headers in headers_list:
            try:
                response = session.get(url, headers=headers, timeout=(5, 10))
                if response.status_code in [200, 302]:
                    log_queue.put(f"{Fore.GREEN}[POTENTIAL VULNERABILITY] {url} with headers {headers} -> {response.status_code}")
                else:
                    print(f"{Fore.YELLOW}[NO VULNERABILITY] {url} with headers {headers} -> {response.status_code}")
            except requests.RequestException as err:
                print(f"{Fore.RED}[ERROR] {url} with headers {headers}: {str(err)}")
    except Exception as e:
        print(f"{Fore.RED}[ERROR] {url}: {str(e)}")

def scan_host_headers(bug_path, urls):
    """Uses threading to scan for Host Header vulnerabilities."""
    log_file_path = f'{bug_path}/HOST_HEADER_LOGS.txt'
    
    log_thread = threading.Thread(target=log_writer, args=(log_file_path,))
    log_thread.start()
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for url in urls:
            executor.submit(test_host_header, url)
    
    log_queue.put(None)
    log_thread.join()

def host_header_scan(bug_path, target):
    """Main function to execute Host Header vulnerability scan."""
    input_file = f"{bug_path}/URL_FOR_{target}.txt"
    
    for urls in read_urls_in_batches(input_file, 10):
        scan_host_headers(bug_path, urls)
