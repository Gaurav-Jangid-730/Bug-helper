import dns.resolver
from Logs import log_vulnerability
from colorama import Fore, init

init(autoreset=True)

# List of known third-party services vulnerable to takeover
TAKEOVER_CANDIDATES = [
    "elasticbeanstalk.com", "s3.amazonaws.com", "airee.ru", "animaapp.io",
    "bitbucket.io", "trydiscourse.com", "furyns.com", "launchrock.com",
    "youtrack.cloud", "ghost.io", "hatenablog.com", "helpjuice.com",
    "helpscoutdocs.com", "helprace.com", "github.io", "herokuapp.com",
    "shopify.com", "wordpress.com", "sendgrid.net", "azurewebsites.net",
    "cloudapp.net", "cloudapp.azure.com", "azure-api.net", "azurehdinsight.net",
    "azureedge.net", "azurecontainer.io", "database.windows.net",
    "azuredatalakestore.net", "search.windows.net", "azurecr.io",
    "redis.cache.windows.net", "servicebus.windows.net", "visualstudio.com",
    "ngrok.io", "readme.io", "52.16.160.97", "s.strikinglydns.com",
    "na-west1.surge.sh", "surveysparrow.com", "read.uberflip.com",
    "worksites.net", "69.164.223.206"
]

def check_cname_takeover(target_dir, subdomain):
    """Check for subdomain takeover via CNAME."""
    try:
        answers = dns.resolver.resolve(subdomain, 'CNAME')
        for rdata in answers:
            cname_target = rdata.target.to_text().strip(".")
            for service in TAKEOVER_CANDIDATES:
                if service in cname_target:
                    message = f"{Fore.GREEN}[!] Potential CNAME Takeover: {subdomain} -> {cname_target}"
                    print(message)
                    log_vulnerability(target_dir, message)
                    return
            print(f"{Fore.BLUE}[*] CNAME: {subdomain} -> {cname_target} (Safe)")
    except dns.resolver.NoAnswer:
        print(f"{Fore.WHITE}[-] No CNAME found for {subdomain}")
    except dns.resolver.NXDOMAIN:
        message = f"{Fore.YELLOW}[!] {subdomain} does not exist (Potential Takeover)"
        print(message)
        log_vulnerability(target_dir, message)
    except Exception as e:
        print(f"{Fore.RED}[!] Error checking CNAME for {subdomain}: {e}")

def check_a_takeover(target_dir, subdomain):
    """Check for subdomain takeover via A records (IP-based takeover)."""
    try:
        answers = dns.resolver.resolve(subdomain, 'A')
        for rdata in answers:
            ip = rdata.to_text()
            if ip in TAKEOVER_CANDIDATES:
                message = f"{Fore.GREEN}[!] Potential A Record Takeover: {subdomain} -> {ip}"
                print(message)
                log_vulnerability(target_dir, message)
            else:
                print(f"{Fore.BLUE}[*] A Record: {subdomain} -> {ip} (Safe)")
    except dns.resolver.NoAnswer:
        print(f"{Fore.WHITE}[-] No A record found for {subdomain}")
    except dns.resolver.NXDOMAIN:
        message = f"{Fore.YELLOW}[!] {subdomain} does not exist (Potential Takeover)"
        print(message)
        log_vulnerability(target_dir, message)
    except Exception as e:
        print(f"{Fore.RED}[!] Error checking A record for {subdomain}: {e}")

def check_ns_takeover(target_dir, subdomain):
    """Check for subdomain takeover via NS (Name Server) records."""
    try:
        answers = dns.resolver.resolve(subdomain, 'NS')
        for rdata in answers:
            ns_target = rdata.to_text().strip(".")
            for service in TAKEOVER_CANDIDATES:
                if service in ns_target:
                    message = f"{Fore.GREEN}[!] Potential NS Takeover: {subdomain} -> {ns_target}"
                    print(message)
                    log_vulnerability(target_dir, message)
                    return
            print(f"{Fore.BLUE}[*] NS Record: {subdomain} -> {ns_target} (Safe)")
    except dns.resolver.NoAnswer:
        print(f"{Fore.WHITE}[-] No NS record found for {subdomain}")
    except dns.resolver.NXDOMAIN:
        message = f"{Fore.YELLOW}[!] {subdomain} does not exist (Potential Takeover)"
        print(message)
        log_vulnerability(target_dir, message)
    except Exception as e:
        print(f"{Fore.RED}[!] Error checking NS record for {subdomain}: {e}")

def check_mx_takeover(target_dir, subdomain):
    """Check for subdomain takeover via MX (Mail Exchange) records."""
    try:
        answers = dns.resolver.resolve(subdomain, 'MX')
        for rdata in answers:
            mx_target = rdata.exchange.to_text().strip(".")
            for service in TAKEOVER_CANDIDATES:
                if service in mx_target:
                    message = f"{Fore.GREEN}[!] Potential MX Takeover: {subdomain} -> {mx_target}"
                    print(message)
                    log_vulnerability(target_dir, message)
                    return
            print(f"{Fore.BLUE}[*] MX Record: {subdomain} -> {mx_target} (Safe)")
    except dns.resolver.NoAnswer:
        print(f"{Fore.WHITE}[-] No MX record found for {subdomain}")
    except dns.resolver.NXDOMAIN:
        message = f"{Fore.YELLOW}[!] {subdomain} does not exist (Potential Takeover)"
        print(message)
        log_vulnerability(target_dir, message)
    except Exception as e:
        print(f"{Fore.RED}[!] Error checking MX record for {subdomain}: {e}")

def subdomain_takeover(target_dir, input_file):
    """Check a list of subdomains for potential takeovers."""
    with open(input_file, 'r') as f:
        subdomains = [line.strip() for line in f]
    
    print(f"{Fore.CYAN}\n🔍 Scanning {len(subdomains)} subdomains for takeover...\n")
    for subdomain in subdomains:
        check_cname_takeover(target_dir, subdomain)
        check_a_takeover(target_dir, subdomain)
        check_ns_takeover(target_dir, subdomain)
        check_mx_takeover(target_dir, subdomain)
