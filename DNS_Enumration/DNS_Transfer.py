import dns.resolver
import dns.query
import dns.zone
import tldextract
import whois
from Logs import log_vulnerability , ipv_46
from Start_up.remove_file import delete_empty_text_files
from colorama import Fore, init

init(autoreset=True)

def get_dns_records(domain, record_type):
    try:
        answers = dns.resolver.resolve(domain, record_type)
        return [answer.to_text() for answer in answers]
    except dns.resolver.NoAnswer:
        return []
    except dns.resolver.NXDOMAIN:
        return []
    except dns.resolver.LifetimeTimeout:
        return []

def check_email_spoofing(target_dir,domain):
    print("\n📧 Checking Email Security...")
    spf = get_dns_records(domain, "TXT")
    dmarc = get_dns_records(f"_dmarc.{domain}", "TXT")
    
    if any("spf1" in record and "+all" in record for record in spf):
        log = f"{Fore.GREEN}[!] Weak SPF policy found for {domain} (allows spoofing)"
        print(log)
        log_vulnerability(target_dir,log)

    if not dmarc:
        print(f"{Fore.RED}[!] No DMARC record found for {domain}")

def check_open_resolver(target_dir, nameservers, checked_nameservers):
    print("\n🌍 Checking Open Resolver...")
    if nameservers in checked_nameservers:
        print(f"{Fore.CYAN}[*] Skipping {ns}, already attempted Recursive DNS.")
        return []
    for ns in nameservers:
        try:
            response = dns.resolver.resolve("google.com", "A", nameserver=ns)
            if response:
                log = f"{Fore.GREEN}[!] Open Resolver Found on {ns}"
                print(log)
                log_vulnerability(target_dir,log)
        except:
            print(f"{Fore.RED}[-] Not an Open Resolver: {ns}")

def find_real_ip(target_dir,domain):
    print("\n🛜 Finding Real IP (Cloudflare Bypass)...")
    subdomains = ["ftp", "mail", "dev", "staging"]
    
    for sub in subdomains:
        subdomain = f"{sub}.{domain}"
        ip_addresses = get_dns_records(subdomain, "A")
        if ip_addresses:
            log = f"{Fore.GREEN}[!] Possible Real IP of {domain}: {ip_addresses}"
            print(log)
            ipv_46(target_dir,log)

def check_internal_ip_leak(target_dir ,domain):
    print("\n🔑 Checking Internal IP Exposure...")
    ip_addresses = get_dns_records(domain, "A")
    
    for ip in ip_addresses:
        if ip.startswith(("10.", "192.168.", "172.16.")):
            log = f"{Fore.GREEN}[!] Internal IP Address Found: {ip}"
            print(log)
            ipv_46(target_dir,log)

def check_expired_domain(target_dir,domain):
    print("\n⌛ Checking for Expired Domains...")
    try:
        details = whois.whois(domain)
        if details.status is None:
            log = f"{Fore.GREEN}[!] Domain {domain} may be Expired and Available for Registration!"
            print(log)
            log_vulnerability(target_dir,log)
    except:
        print("[-] WHOIS lookup failed")

def get_nameservers(target_dir,domain):
    print("\n🛠 Checking NS Records...")
    ns_records = get_dns_records(domain, "NS")
    if ns_records:
        print(f"{Fore.BLUE}[!] Nameservers Found: {ns_records}")
        return ns_records
    else:
        log = f"{Fore.GREEN}[!] No NS records found for {domain}, possible misconfiguration!"
        print(log)
        log_vulnerability(target_dir,log)
        return []

def get_root_domain(domain):
    ext = tldextract.extract(domain)
    return f"{ext.domain}.{ext.suffix}"

def get_ipv6(ns, checked_nameservers):
    """Resolve IPv6 for a nameserver"""
    if ns in checked_nameservers:
        print(f"{Fore.CYAN}[*] Skipping {ns}, already attempted Get IPv6.")
        return []
    try:
        ipv6 = dns.resolver.resolve(ns, 'AAAA')
        return [str(ip) for ip in ipv6]
    except:
        return []

def check_zone_transfer(ns, domain, target_dir, checked_nameservers):
    """Try Zone Transfer on the given NS"""
    if ns in checked_nameservers:
        print(f"{Fore.CYAN}[*] Skipping {ns}, already attempted Zone Transfer.")
        return []
    try:
        ns_ip = dns.resolver.resolve(ns, 'A')[0].to_text()
        print(f"{Fore.YELLOW}[*] Trying Zone Transfer on {ns} ({ns_ip})")
        
        # Timeout to prevent hanging
        zone = dns.zone.from_xfr(dns.query.xfr(ns_ip, domain, timeout=5))
        
        log = f"\n{Fore.GREEN}[✔] Zone Transfer SUCCESS: {domain} via {ns}\n"
        print(log)
        log_vulnerability(target_dir,log)
        checked_nameservers.add(ns)
        return [name.to_text() for name, _ in zone.nodes.items()]
    
    except dns.exception.FormError:
        print(f"{Fore.RED}[-] Zone Transfer not allowed on {ns} for {domain}")
    except dns.exception.Timeout:
        print(f"{Fore.RED}[-] Zone Transfer timed out on {ns} for {domain}")
    except Exception as e:
        print(f"{Fore.RED}[-] Error in Zone Transfer: {e}")
    checked_nameservers.add(ns)
    return []


def check_recursive_dns(ns, checked_nameservers):
    """Check if DNS server allows recursive queries"""
    if ns in checked_nameservers:
        print(f"{Fore.CYAN}[*] Skipping {ns}, already attempted Recursive DNS.")
        return []
    try:
        query = dns.message.make_query('www.google.com', dns.rdatatype.A)
        response = dns.query.udp(query, ns, timeout=2)
        if response.answer:
            print(f"{Fore.BLUE}[!] Open Recursive DNS found: {ns}")
            return True
    except:
        pass
    return False

def DNS_transfer(target_dir):
    input_file = f'{target_dir}/resolved-final-subdomains.txt'
    with open(input_file, 'r') as f:
        subdomains = [line.strip() for line in f]

    checked_nameservers = set()
    
    for domain in subdomains:
        root_domain = get_root_domain(domain)
        print(f"\n{Fore.YELLOW}[*] Scanning {root_domain}")
        
        try:
            name_servers = get_nameservers(target_dir,root_domain)
            find_real_ip(target_dir,domain)
            check_internal_ip_leak(target_dir,domain)
            check_email_spoofing(target_dir,domain)
            check_expired_domain(target_dir,domain)

        except dns.resolver.LifetimeTimeout:
            print(f"{Fore.RED}[-] NS lookup timed out for {root_domain}")
            continue  # Skip this domain and move to the next one

        for ns in name_servers:
            try:
                ipv6 = get_ipv6(ns, checked_nameservers)
                if ipv6:
                    log = f"{Fore.GREEN}[*] IPv6 Found for {ns}: {ipv6}"
                    print(log)
                    ipv_46(target_dir,log)
                
                check_zone_transfer(ns, domain, target_dir, checked_nameservers)
                check_recursive_dns(ns, checked_nameservers)
                check_open_resolver(target_dir,ns,checked_nameservers)
            except dns.resolver.LifetimeTimeout:
                print(f"{Fore.RED}[-] DNS query timed out for {ns}, skipping...")
    delete_empty_text_files(target_dir)