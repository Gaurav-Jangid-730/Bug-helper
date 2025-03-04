import requests
import threading
import concurrent.futures
from Runner.Runner import run_command
from setup.remove_file import delete_empty_text_files
from urllib.parse import urlparse, urlencode
from colorama import Fore, Style , init

init(autoreset=True)

THREADS = 100
print_lock = threading.Lock()
# Common redirect parameters
redirect_params = [
    "redirect", "url", "next", "return", "r", "u", "goto", "target",
    "forward", "continue", "checkout_url", "dest", "destination", "go",
    "image_url", "redir", "redirect_uri", "redirect_url", "return_path",
    "return_to", "returnTo", "rurl", "view"
]

redirect_paths = [
    "/redirect/", "/go/", "/continue/", "/checkout/", "/out/", "/exit/",
    "/track/", "/trackback/", "/leave/", "/away/", "/visit/", "/r/", "/", 
    "/cgi-bin/redirect.cgi?", "/out?", "/login?to="
]

def filter_redirect_urls(bug_path,urls):
    """Filter URLs that contain redirect-related parameters."""
    print(f"{Fore.BLUE}[+] Filtering URLs with redirect parameters...")
    redirect_urls = [url for url in urls if any(param in url for param in redirect_params)]
    with open(f"{bug_path}/redirect_urls.txt", "w") as f:
        f.write("\n".join(redirect_urls))
    return redirect_urls

def test_url(url, payload, headers, bug_path):
    """Test a single URL for open redirects (query-based & path-based)."""
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    # === Query Parameter-Based Injection ===
    new_query_params = {}
    for param, values in query_params.items():
        if param.lower() in redirect_params:  # Check if it's a redirect parameter
            new_query_params[param] = [payload]
        else:
            new_query_params[param] = values

    # Build new query string
    new_query = urlencode(new_query_params, doseq=True)

    # === Path-Based Injection ===
    modified_path = parsed_url.path
    for redirect_path in redirect_paths:
        if redirect_path in parsed_url.path:  # If path contains a redirect pattern
            modified_path = parsed_url.path.replace(redirect_path, f"{redirect_path}{payload}")

    # Construct modified test URL
    test_url = urlunparse((parsed_url.scheme, parsed_url.netloc, modified_path, parsed_url.params, new_query, parsed_url.fragment))

    # Send request
    try:
        response = requests.get(test_url, headers=headers, allow_redirects=False)
        if response.status_code in [301, 302] and "evil.com" in response.headers.get("Location", ""):
            with print_lock:
                print(f"{Fore.GREEN}[!] Open Redirect Found: {test_url}")  # Green Text Output
                with open(f'{bug_path}/LOGS.txt','a') as f:
                    f.write(f"\n{Fore.GREEN}[!] Open Redirect Found: {test_url}\n")
            return test_url
    except requests.exceptions.RequestException as e:
        with print_lock:
            print(f"{Fore.RED}[-] Error testing {test_url}: {e}")  # Red Text Output
    return None

def test_redirects(redirect_urls , bug_path):
    """Test multiple URLs for open redirect vulnerabilities using threads."""
    print(f"{Fore.BLUE}[+] Testing for open redirects...{Style.RESET_ALL}")
    vulnerable_urls = []
    headers = {"User-Agent": "Mozilla/5.0"}
    # Define payloads for open redirect testing
    payloads = []
    with open(f'Open_redirect/payloads.txt', 'r') as f:
        payloads = [line.strip() for line in f]
    # Prepare tasks for threading
    tasks = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
        for url in redirect_urls:       
            for payload in payloads:
                tasks.append(executor.submit(test_url, url, payload, headers, bug_path))
        # Collect results
        for future in concurrent.futures.as_completed(tasks):
            result = future.result()
            if result:
                vulnerable_urls.append(result)

    if vulnerable_urls:
        print(f"{Fore.GREEN}[+] {len(vulnerable_urls)} Open Redirects Found!{Style.RESET_ALL}")
    
    return vulnerable_urls

def open_redirect(bug_path,target):
    input_file = f"{bug_path}/URL_FOR_{target}.txt"
    urls = []
    with open(input_file, 'r') as f:
        urls = list([line.strip() for line in f])
    redirect_urls = filter_redirect_urls(bug_path,urls)
    vulnerable_urls = test_redirects(redirect_urls , bug_path)
    with open(f"{bug_path}/open_redirect_vulnerable_urls.txt", "w") as f:
        f.write("\n".join(vulnerable_urls))
    print(f"{Fore.GREEN}[+] Scan Completed! Check open_redirect_vulnerable_urls.txt")
    with open(f"{bug_path}/LOGS.txt",'a') as f:
        f.write(f"\n{Fore.GREEN}[+] Check File open_redirect_vulnerable_urls.txt For Open Redirect Vulnerablity\n")
    delete_empty_text_files(bug_path)