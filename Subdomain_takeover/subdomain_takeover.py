import dns.resolver
from colorama import Fore, init

init(autoreset=True)

# List of known third-party services vulnerable to takeover
TAKEOVER_CANDIDATES = [
    "elasticbeanstalk.com",
    "s3.amazonaws.com",
    "airee.ru",
    "animaapp.io",
    "bitbucket.io",
    "trydiscourse.com",
    "furyns.com",
    "launchrock.com"
    "youtrack.cloud",
    "ghost.io",
    "hatenablog.com",
    "helpjuice.com",
    "helpscoutdocs.com",
    "helprace.com",
    "github.io",
    "s3.amazonaws.com",
    "herokuapp.com",
    "shopify.com",
    "wordpress.com",
    "sendgrid.net",
    "azurewebsites.net",
    "cloudapp.net",
    "cloudapp.azure.com",
    "azurewebsites.net", 
    "blob.core.windows.net",
    "cloudapp.azure.com", 
    "azure-api.net", 
    "azurehdinsight.net", 
    "azureedge.net", 
    "azurecontainer.io", 
    "database.windows.net", 
    "azuredatalakestore.net", 
    "search.windows.net",
    "azurecr.io", 
    "redis.cache.windows.net", 
    "azurehdinsight.net", 
    "servicebus.windows.net", 
    "visualstudio.com",
    "ngrok.io",
    "readme.io",
    "52.16.160.97",
    "s.strikinglydns.com",
    "na-west1.surge.sh",
    "surveysparrow.com",
    "read.uberflip.com",
    "wordpress.com",
    "worksites.net", 
    "69.164.223.206"
]

def check_cname_takeover(target_dir,subdomain):
    """Check if a subdomain has a dangling CNAME pointing to a third-party service."""
    try:
        answers = dns.resolver.resolve(subdomain, 'CNAME')
        for rdata in answers:
            cname_target = rdata.target.to_text().strip(".")
            for service in TAKEOVER_CANDIDATES:
                if service in cname_target:
                    print(f"{Fore.GREEN}[!] Potential Takeover: {subdomain} -> {cname_target}")
                    with open(f"{target_dir}/LOGS.txt",'a') as f:
                        f.write(f"\n{Fore.GREEN}[!] Potential Takeover: {subdomain} -> {cname_target}\n")
                    return cname_target
            print(f"{Fore.BLUE}[*] CNAME: {subdomain} -> {cname_target} (Safe)")
    except dns.resolver.NoAnswer:
        print(f"{Fore.WHITE}[-] No CNAME found for {subdomain}")
    except dns.resolver.NXDOMAIN:
        print(f"{Fore.YELLOW}[!] {subdomain} does not exist (Potentially Vulnerable)")
        with open(f"{target_dir}/LOGS.txt",'a') as f:
                f.write(f"\n{Fore.YELLOW}[!] {subdomain} does not exist (Potentially Vulnerable)\n")
    except Exception as e:
        print(f"{Fore.RED}[!] Error checking {subdomain}: {e}")

def subdomain_takeover(target_dir,input_file):
    with open(input_file, 'r') as f:
        subdomains = [line.strip() for line in f]
    
    print(f"{Fore.CYAN}\n🔍 Scanning {len(subdomains)} subdomains for takeover...\n")
    for subdomain in subdomains:
        check_cname_takeover(target_dir,subdomain)

