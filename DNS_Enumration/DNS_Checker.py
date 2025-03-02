from Runner.Runner import run_section
from DNS_Enumration.DNS_Transfer import main
from colorama import Fore, Style, init

init(autoreset=True)

def dns_enum(target_dir):
    input_file = f'{target_dir}/resolved-final-subdomains.txt'
    subdomains = open(input_file,"r")
    for subdomain in subdomains.readlines():
        subdomain = subdomain.strip()
        commands = [
            f'dig {subdomain} +short > {target_dir}/DNS/dig-ip-{subdomain}.txt',
            f'dig {subdomain} ANY > {target_dir}/DNS/dig-{subdomain}.txt',
            f'dig ns {subdomain} +short > {target_dir}/DNS/dig-ns-{subdomain}.txt',
            f'host -a {subdomain} > {target_dir}/DNS/host-{subdomain}.txt',
            f'dnsrecon -d {subdomain} -t axfr > {target_dir}/DNS/dnsrecon-{subdomain}.txt'
        ]
        print(f"\n{Fore.MAGENTA}{'='*80}\n{'='*80}")
        print(f"Running for {subdomain} ...")
        print(f"\n{Fore.MAGENTA}{'='*80}\n{'='*80}")
        run_section(f'Running Dig , Host , Dnsrecon and Fierce cammand',commands)
        input_ns_file = f'{target_dir}/DNS/dig-ns-{subdomain}.txt'
        ns_file = open(input_ns_file,"r")
        for ns in ns_file.readlines():
            ns = ns.strip()
            command = [
                f'dig axfr {subdomain} @{ns} > {target_dir}/DNS/NS/{subdomain}-{ns}.txt',
                f'fierce --dns-servers {ns} > {target_dir}/DNS/NS/fierce-{subdomain}-{ns}.txt'
            ]
            run_section(f'Finding dns transfer in {subdomain}',command)
    main(input_file)