from Runner.Runner import run_section

def subdomain_finding(target, target_dir, enable_bruteforce):
    commands = [
        f"sublist3r -d {target} -o {target_dir}/sub-{target}.txt",
        f"findomain -t {target} -o -v",
        f"subfinder -d {target} -all -o {target_dir}/sub-find-{target}.txt",
        f"assetfinder --subs-only {target} > {target_dir}/asset-{target}.txt",
        f"mv {target}.txt {target_dir}/findomain-{target}.txt",
    ]
    
    if enable_bruteforce:
        brute_force_commands = [
            f"findomain -t {target} -w /usr/share/wordlists/SecLists/Discovery/DNS/n0kovo_subdomains.txt -o -v",
            f"mv {target}.txt {target_dir}/findomain-brute-{target}.txt",
        ]
        commands.extend(brute_force_commands)
    
    commands.extend([
        f"cat {target_dir}/sub-{target}.txt {target_dir}/asset-{target}.txt {target_dir}/sub-find-{target}.txt {target_dir}/findomain-{target}.txt {'{target_dir}/findomain-brute-{target}.txt' if enable_bruteforce else ''} | sort -u > {target_dir}/final-{target}-subdomains.txt",
        f"awk '{{print tolower($0)}}' {target_dir}/final-{target}-subdomains.txt | sort -u > {target_dir}/subdomains-list.txt",
        f"dnsx -l {target_dir}/subdomains-list.txt -o {target_dir}/resolved-final-subdomains.txt",
        f"rm {target_dir}/subdomains-list.txt {target_dir}/sub-{target}.txt {target_dir}/asset-{target}.txt {target_dir}/sub-find-{target}.txt {target_dir}/findomain-{target}.txt {'{target_dir}/findomain-brute-{target}.txt' if enable_bruteforce else ''} {target_dir}/final-{target}-subdomains.txt"
    ])
    
    run_section("Subdomain Enumeration, Discovery, Bruteforce, and Resolving", commands)
