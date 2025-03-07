from Runner.Runner import run_section
from subdomain_Enumatration.Virustotal import get_subdomains
import os
def subdomain_finding(target, target_dir, enable_bruteforce):
    commands = [
        f"sublist3r -d {target} -o {target_dir}/sub-{target}.txt",
        f"findomain -t {target} -o -v",
        f"subfinder -d {target} -all -o {target_dir}/sub-find-{target}.txt",
        f"assetfinder --subs-only {target} > {target_dir}/asset-{target}.txt",
        f"mv {target}.txt {target_dir}/findomain-{target}.txt",
    ]
    virustotal = False
    file_path = "virustotal_api.txt"
    if os.path.exists(file_path):
        virustotal = True
        with open(file_path, "r") as file:
            api_key = file.read().strip()
        print("[+] Finding Subdomains Using VirusTotal.")
        get_subdomains(target, api_key)
    else:
        print("[-] VirusTotal Is Not Integrated.")

    if enable_bruteforce:
        brute_force_commands = [
            f"findomain -t {target} -w /usr/share/wordlists/SecLists/Discovery/DNS/n0kovo_subdomains.txt -o -v",
            f"mv {target}.txt {target_dir}/findomain-brute-{target}.txt",
        ]
        commands.extend(brute_force_commands)
    
    commands.extend([
        f"cat {'{target_dir}/{target}_subdomains.txt' if virustotal else ''} {target_dir}/sub-{target}.txt {target_dir}/asset-{target}.txt {target_dir}/sub-find-{target}.txt {target_dir}/findomain-{target}.txt {'{target_dir}/findomain-brute-{target}.txt' if enable_bruteforce else ''} | sort -u > {target_dir}/final-{target}-subdomains.txt",
        f"awk '{{print tolower($0)}}' {target_dir}/final-{target}-subdomains.txt | sort -u > {target_dir}/subdomains-list.txt",
        f"dnsx -l {target_dir}/subdomains-list.txt -o {target_dir}/resolved-final-subdomains.txt",
        f"rm {'{target_dir}/{target}_subdomains.txt' if virustotal else ''} {target_dir}/subdomains-list.txt {target_dir}/sub-{target}.txt {target_dir}/asset-{target}.txt {target_dir}/sub-find-{target}.txt {target_dir}/findomain-{target}.txt {'{target_dir}/findomain-brute-{target}.txt' if enable_bruteforce else ''} {target_dir}/final-{target}-subdomains.txt"
    ])

    run_section("Subdomain Enumeration, Discovery, Bruteforce, and Resolving", commands)
