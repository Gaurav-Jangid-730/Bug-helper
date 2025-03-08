import os
from concurrent.futures import ThreadPoolExecutor
from Runner.Runner import run_section
from Start_up.Ip_placer import ip_placer

def Url_finding(target, target_dir):
    subdomain_file = f"{target_dir}/resolved_final_subdomains.txt"
    output_file = f"{target_dir}/URL_FOR_{target}.txt"

    commands = [
        f'cpulimit -l 85 --foreground -- waymore -i {target} -oU {target_dir}/waymore_results.txt',
        f'cat {subdomain_file} | gau --subs > {target_dir}/gau_results.txt',
        f'echo {target} | katana -ps -pss waybackarchive,commoncrawl,alienvault -f qurl >> {target_dir}/waymore_results.txt',
        f'cat {subdomain_file} | waybackurls > {target_dir}/waybackurls.txt',
        f'echo {target} | hakrawler -d 3 -u > {target_dir}/hakrawler_results.txt',
        f'cat {target_dir}/gau_results.txt {target_dir}/waybackurls.txt {target_dir}/hakrawler_results.txt {target_dir}/waymore_results.txt | uro | sort -u > {output_file}',
        f'rm {target_dir}/gau_results.txt {target_dir}/waybackurls.txt {target_dir}/hakrawler_results.txt {target_dir}/waymore_results.txt',
    ]
    run_section("Extracting and Filtering URLs", commands)
    ip_placer(target, target_dir)

    # Use the processed file if it exists
    final_file = f"{target_dir}/processed-urls.txt" if os.path.exists(f"{target_dir}/processed-urls.txt") else output_file

    # Filtering interesting URLs
    filters = {
        "interesting_urls.txt": r'\.php|\.aspx|\.jsp|\.html|\.txt|\.bak|\.zip',
        "api_endpoints.txt": "/api/",
        "backups.txt": r'\.bak|\.old|\.log|\.sql|\.zip|\.gz|\.tar',
        "redirect_urls.txt": "redirect",
        "directories.txt": r"sed -r 's|(http[s]?://[^/]+).*|\1|' | sort -u",
        "sensitive_files.txt": r'\.env|\.config|\.json|\.yaml|\.yml'
    }

    payloads = {
        "xss-url.txt": "gf xss",
        "sqli-url.txt": "gf sqli",
        "lfi-url.txt": "gf lfi",
        "ssrf-url.txt": "gf ssrf",
        "idor-url.txt": "gf idor",
        "ssti-url.txt": "gf ssti"
    }

    # Running filtering commands in parallel
    filtering_commands = [f'cat {final_file} | grep -E "{regex}" > {target_dir}/interest/{file}' for file, regex in filters.items()]
    filtering_commands += [f'cat {final_file} | {gf_command} > {target_dir}/payloads/{file}' for file, gf_command in payloads.items()]
    run_section("Filtering interesting URLs and Payloads", filtering_commands)