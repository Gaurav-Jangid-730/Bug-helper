import os
import re
import requests
import subprocess
from Runner.Runner import run_command
from setup.remove_file import delete_empty_text_files
from urllib.parse import urlparse, urlencode
from colorama import Fore, init

init(autoreset=True)

# Define payloads for open redirect testing
payloads = [
    "http://evil.com", "https://evil.com", "//evil.com", 
    "\\evil.com", "///evil.com", "https:\\\\evil.com",
    "%2F%2Fevil.com", "%5Cevil.com", "%68%74%74%70%73%3A%2F%2Fevil.com"
]

# Common redirect parameters
redirect_params = ["redirect", "url", "next", "return", "r", "u", "goto", "target", "forward", "continue"]

def fetch_urls(domain):
    """Find historical URLs using waybackurls & gau."""
    print(f"{Fore.BLUE}[+] Fetching URLs from Wayback Machine and GAU...")
    wayback_urls = run_command(f"echo {domain} | waybackurls")
    gau_urls = run_command(f"echo {domain} | gau")
    urls = list(set(wayback_urls + gau_urls))  # Remove duplicates
    with open("all_urls.txt", "w") as f:
        f.write("\n".join(urls))
    return urls

def filter_redirect_urls(bug_path,urls):
    """Filter URLs that contain redirect-related parameters."""
    print(f"{Fore.BLUE}[+] Filtering URLs with redirect parameters...")
    redirect_urls = [url for url in urls if any(param in url for param in redirect_params)]
    with open(f"{bug_path}/redirect_urls.txt", "w") as f:
        f.write("\n".join(redirect_urls))
    return redirect_urls

def test_redirects(redirect_urls):
    """Test URLs for open redirect vulnerabilities."""
    print(f"{Fore.BLUE}[+] Testing for open redirects...")
    vulnerable_urls = []
    headers = {"User-Agent": "Mozilla/5.0"}
    
    for url in redirect_urls:
        parsed_url = urlparse(url)
        query = parsed_url.query
        
        for payload in payloads:
            for param in redirect_params:
                if param in query:
                    new_query = re.sub(f'({param}=)[^&]+', f'\1{payload}', query)
                    test_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?{new_query}"
                    
                    try:
                        response = requests.get(test_url, headers=headers, allow_redirects=False)
                        if response.status_code in [301, 302] and "evil.com" in response.headers.get("Location", ""):
                            print(f"{Fore.GREEN}[!] Open Redirect Found: {test_url}")
                            vulnerable_urls.append(test_url)
                    except requests.exceptions.RequestException as e:
                        print(f"{Fore.RED}[-] Error testing {test_url}: {e}")
    if len(vulnerable_urls)!=0:
        print(f"{Fore.GREEN}[+] {len(vulnerable_urls)} Open Redirects Found!")
    return vulnerable_urls

def open_redirect(bug_path,input_file):
    with open(input_file, 'r') as f:
        domains = [line.strip() for line in f]
    urls = []
    for domain in domains:
        urls.extend(fetch_urls(domain))
        redirect_urls = filter_redirect_urls(bug_path,urls)
        vulnerable_urls = test_redirects(redirect_urls)
        with open(f"{bug_path}/{domain}_vulnerable_urls.txt", "w") as f:
            f.write("\n".join(vulnerable_urls))
        print(f"{Fore.GREEN}[+] Scan Completed! Check {domain}_vulnerable_urls.txt")
        with open(f"{bug_path}/LOGS.txt",'a') as f:
            f.write(f"{Fore.GREEN}[+] Check File {domain}_vulnerable_urls.txt For Open Redirect Vulnerablity")
    delete_empty_text_files(bug_path)