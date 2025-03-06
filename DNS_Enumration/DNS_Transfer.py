import dns.resolver
import dns.query
import dns.zone
import tldextract
from setup.remove_file import delete_empty_text_files
from colorama import Fore, init

init(autoreset=True)

def get_root_domain(domain):
    ext = tldextract.extract(domain)
    return f"{ext.domain}.{ext.suffix}"

def get_nameservers(domain):
    """Find name servers for the domain"""
    try:
        ns_records = dns.resolver.resolve(domain, 'NS')
        return [str(ns) for ns in ns_records]
    except Exception as e:
        print(f"{Fore.RED}[!] Failed to get NS for {domain}: {e}")
        return []

def get_ipv6(ns):
    """Resolve IPv6 for a nameserver"""
    try:
        ipv6 = dns.resolver.resolve(ns, 'AAAA')
        return [str(ip) for ip in ipv6]
    except:
        return []

def check_zone_transfer(ns, domain, target_dir):
    """Try Zone Transfer on the given NS"""
    try:
        ns_ip = dns.resolver.resolve(ns, 'A')[0].to_text()
        print(f"{Fore.YELLOW}[*] Trying Zone Transfer on {ns} ({ns_ip})")
        
        # Timeout to prevent hanging
        zone = dns.zone.from_xfr(dns.query.xfr(ns_ip, domain, timeout=5))
        
        print(f"\n{Fore.GREEN}[✔] Zone Transfer SUCCESS: {domain} via {ns}\n")
        with open(f'{target_dir}/LOGS.txt', 'a') as f:
            f.write(f"\n[✔] Zone Transfer SUCCESS: {domain} via {ns}\n")
        return [name.to_text() for name, _ in zone.nodes.items()]
    
    except dns.exception.FormError:
        print(f"{Fore.RED}[-] Zone Transfer not allowed on {ns} for {domain}")
    except dns.exception.Timeout:
        print(f"{Fore.RED}[-] Zone Transfer timed out on {ns} for {domain}")
    except Exception as e:
        print(f"{Fore.RED}[-] Error in Zone Transfer: {e}")
    
    return []


def check_recursive_dns(ns):
    """Check if DNS server allows recursive queries"""
    try:
        query = dns.message.make_query('www.google.com', dns.rdatatype.A)
        response = dns.query.udp(query, ns, timeout=2)
        if response.answer:
            print(f"{Fore.BLUE}[!] Open Recursive DNS found: {ns}")
            return True
    except:
        pass
    return False

def check_cname_hijack(subdomain):
    resolver = dns.resolver.Resolver()
    resolver.timeout = 10  # Increase timeout from 5 to 10 seconds
    resolver.lifetime = 15  # Extend total lifetime for queries
    resolver.nameservers = ["8.8.8.8", "1.1.1.1"]  # Use Google & Cloudflare DNS

    try:
        answers = resolver.resolve(subdomain, 'CNAME')
        for rdata in answers:
            cname_target = rdata.target.to_text()
            if "sendgrid.net" in cname_target:  # Example third-party service
                print(f"{Fore.BLUE}[!] Potential CNAME Hijacking: {subdomain} -> {cname_target}")
    except dns.resolver.NoAnswer:
        pass
    except dns.resolver.NXDOMAIN:
        print(f"{Fore.BLUE}[!] {subdomain} might be a dangling CNAME")
    except dns.resolver.LifetimeTimeout:
        print(f"{Fore.RED}[-] CNAME lookup timed out for {subdomain}, try again later.")


def DNS_transfer(target_dir):
    input_file = f'{target_dir}/resolved-final-subdomains.txt'
    with open(input_file, 'r') as f:
        subdomains = [line.strip() for line in f]
    
    for domain in subdomains:
        root_domain = get_root_domain(domain)
        print(f"\n{Fore.YELLOW}[*] Scanning {root_domain}")
        
        try:
            name_servers = get_nameservers(root_domain)
        except dns.resolver.LifetimeTimeout:
            print(f"{Fore.RED}[-] NS lookup timed out for {root_domain}")
            continue  # Skip this domain and move to the next one

        for ns in name_servers:
            try:
                ipv6 = get_ipv6(ns)
                if ipv6:
                    print(f"{Fore.YELLOW}[*] IPv6 Found for {ns}: {ipv6}")

                check_zone_transfer(ns, domain, target_dir)
                check_recursive_dns(ns)
                check_cname_hijack(domain)
            except dns.resolver.LifetimeTimeout:
                print(f"{Fore.RED}[-] DNS query timed out for {ns}, skipping...")
        delete_empty_text_files(target_dir)
