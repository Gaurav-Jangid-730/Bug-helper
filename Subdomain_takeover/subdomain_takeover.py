import dns.resolver
import argparse
from colorama import Fore, init

init(autoreset=True)

# List of known third-party services vulnerable to takeover
TAKEOVER_CANDIDATES = [
    "github.io",
    "s3.amazonaws.com",
    "herokuapp.com",
    "shopify.com",
    "wordpress.com",
    "sendgrid.net",
    "azurewebsites.net",
]

def check_cname_takeover(subdomain):
    """Check if a subdomain has a dangling CNAME pointing to a third-party service."""
    try:
        answers = dns.resolver.resolve(subdomain, 'CNAME')
        for rdata in answers:
            cname_target = rdata.target.to_text().strip(".")
            for service in TAKEOVER_CANDIDATES:
                if service in cname_target:
                    print(f"{Fore.BLUE}[!] Potential Takeover: {subdomain} -> {cname_target}")
                    return cname_target
            print(f"{Fore.GREEN}[*] CNAME: {subdomain} -> {cname_target} (Safe)")
    except dns.resolver.NoAnswer:
        print(f"{Fore.YELLOW}[-] No CNAME found for {subdomain}")
    except dns.resolver.NXDOMAIN:
        print(f"{Fore.RED}[!] {subdomain} does not exist (Potentially Vulnerable)")
    except Exception as e:
        print(f"{Fore.RED}[!] Error checking {subdomain}: {e}")

def main(input_file):
    with open(input_file, 'r') as f:
        subdomains = [line.strip() for line in f]
    
    print(f"{Fore.CYAN}\n🔍 Scanning {len(subdomains)} subdomains for takeover...\n")
    for subdomain in subdomains:
        check_cname_takeover(subdomain)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Subdomain Takeover Scanner")
    parser.add_argument("-f", "--file", required=True, help="File containing subdomains")
    args = parser.parse_args()
    main(args.file)
