import os
from Runner.Runner import run_section
from setup.Ip_placer import ip_placer

def Url_finding(target, target_dir):
    commands = [
        f'cpulimit -l 85 -- waymore -i {target} -oU {target_dir}/waymore_results.txt',
        f'echo {target} | katana -ps -pss waybackarchive,commoncrawl,alienvault -f qurl >> {target_dir}/waymore_results.txt',
        f'cat {target_dir}/resolved-final-subdomains.txt | waybackurls > {target_dir}/urls-{target}.txt',
        f'echo {target} | hakrawler -d 3 -u > {target_dir}/crawled_urls.txt',
        f'cat {target_dir}/urls-{target}.txt {target_dir}/crawled_urls.txt {target_dir}/waymore_results.txt | uro > {target_dir}/URL_FOR_{target}.txt',
        f'rm {target_dir}/urls-{target}.txt {target_dir}/crawled_urls.txt {target_dir}/waymore_results.txt',
    ]
    run_section("Finding Url using waybackurls , katana , waymore urls , crawling", commands)
    ip_placer(target,target_dir)
    if os.path.exists(f'{target_dir}/processed-urls.txt'):
        file = f'{target_dir}/processed-urls.txt'
    else:
        file = f'{target_dir}/URL_FOR_{target}.txt'
    commands_2 = [
        f'cat {file} | grep -E "\.php|\.aspx|\.jsp|\.html|\.txt|\.bak|\.zip" > {target_dir}/interest/interesting_urls.txt',
        f'cat {file} | grep "/api/" > {target_dir}/interest/api_endpoints.txt',
        f'cat {file} | grep -E "\.bak|\.old|\.log|\.sql|\.zip|\.gz|\.tar" > {target_dir}/interest/backups.txt',
        f'cat {file} | grep "redirect" > {target_dir}/interest/redirect_urls.txt',
        f"cat {file} | sed -r 's|(http[s]?://[^/]+).*|\1|' | sort -u > {target_dir}/interest/directories.txt",
        f'cat {file} | grep -E "\.env|\.config|\.json|\.yaml|\.yml" > {target_dir}/interest/sensitive_files.txt',
        f'cat {file} | gf xss > {target_dir}/payloads/xss-url.txt',
        f'cat {file} | gf sqli > {target_dir}/payloads/sqli-url.txt',
        f'cat {file} | gf lfi > {target_dir}/payloads/lfi-url.txt',
        f'cat {file} | gf ssrf > {target_dir}/payloads/ssrf-url.txt',
        f'cat {file} | gf idor > {target_dir}/payloads/idor-url.txt',
        f'cat {file} | gf ssti > {target_dir}/payloads/ssti-url.txt',
    ]
    run_section("Filtering for sqli , lfi , ssrt , xss , idor , ssti", commands_2)