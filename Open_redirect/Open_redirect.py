import requests
import threading
import os
import urllib.parse
from Start_up.remove_file import delete_empty_text_files
from colorama import Fore, Style, init

init(autoreset=True)

# Common redirect parameters
redirect_params = [
    "redirect", "url", "next", "return", "r", "u", "goto", "target",
    "forward", "continue", "checkout_url", "dest", "destination", "go",
    "image_url", "redir", "redirect_uri", "redirect_url", "return_path",
    "return_to", "returnTo", "rurl", "view"
]

# Common redirect paths
redirect_paths = [
    "/redirect/", "/go/", "/continue/", "/checkout/", "/out/", "/exit/",
    "/track/", "/trackback/", "/leave/", "/away/", "/visit/", "/r/",
    "/", "/cgi-bin/redirect.cgi?", "/out?", "/login?to="
]

# Function to filter URLs containing redirection parameters or paths
def filter_urls(urls):
    filtered = []
    for url in urls:
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
def test_redirect(bug_path ,url, payload):
    try:
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        with open(f'{bug_path}/LOGS.txt', 'a') as f:
        # Test query-based injection
            for param in query_params:
                if param in redirect_params:
                    injected_url = url.replace(query_params[param][0], urllib.parse.quote_plus(payload))
                    response = requests.get(injected_url, allow_redirects=False)
                    print(f"\n{Fore.GREEN}[QUERY] {injected_url} -> {response.status_code}\n")
                    f.write(f"\n{Fore.GREEN}[QUERY] {injected_url} -> {response.status_code}\n")

        # Test path-based injection
            for path in redirect_paths:
                if path in url:
                    injected_url = url.rstrip("/") + "/" + urllib.parse.quote_plus(payload)
                    response = requests.get(injected_url, allow_redirects=False)
                    print(f"\n{Fore.GREEN}[PATH] {injected_url} -> {response.status_code}\n")
                    f.write(f"\n{Fore.GREEN}[PATH] {injected_url} -> {response.status_code}\n")

    except Exception as e:
        print(f"{Fore.RED}[ERROR] {url}: {str(e)}")

# Function to start scanning with threading
def scan_urls(bug_path, urls, payloads):
    threads = []
    for url in urls:
        for payload in payloads:
            thread = threading.Thread(target=test_redirect, args=(bug_path, url, payload))
            threads.append(thread)
            thread.start()

    for thread in threads:
        thread.join()

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
        print(f"{Fore.RED}[-] Payloads fIle at path {file_path} is not found!{Style.RESET_ALL}")
        return

    # Filter relevant URLs
    filtered_urls = filter_urls(urls)
    print(f"{Fore.BLUE}Filtered {len(filtered_urls)} potential redirect URLs from {len(urls)} total URLs.")

    # Scan for open redirects
    scan_urls(bug_path,filtered_urls, payloads)
    delete_empty_text_files(bug_path)