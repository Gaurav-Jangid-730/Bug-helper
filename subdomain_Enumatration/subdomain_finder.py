from Runner.Runner import run_section
from subdomain_Enumatration.Virustotal import get_subdomains
import os

def safe_read_file(filepath):
    """Reads a file if it exists, returns a list of lines, else returns an empty list."""
    if os.path.exists(filepath):
        with open(filepath, "r") as file:
            return file.readlines()
    return []

def safe_remove_files(files):
    """Removes files if they exist."""
    for file in files:
        if os.path.exists(file):
            os.remove(file)

def merge_and_sort_files(output_file, *input_files):
    """Merges multiple existing files, sorts lines uniquely, and writes to an output file."""
    unique_lines = set()
    
    for file in input_files:
        if os.path.exists(file):  # Only read files that exist
            with open(file, "r") as f:
                unique_lines.update(line.strip() for line in f.readlines())

    # Always create the output file, even if no input files exist
    with open(output_file, "w") as out_file:
        out_file.writelines(line + '\n' for line in sorted(unique_lines, key=str.lower))

    print(f"[INFO] Merged {len(unique_lines)} unique lines into {output_file}")

def subdomain_finding(target, target_dir, enable_bruteforce):
    commands = [
        f"sublist3r -d {target} -o {target_dir}/sub-{target}.txt",
        f"findomain -t {target} -o -v",
        f"subfinder -d {target} -all -o {target_dir}/sub-find-{target}.txt",
        f"assetfinder --subs-only {target} > {target_dir}/asset-{target}.txt",
        f"mv {target}.txt {target_dir}/findomain-{target}.txt",
    ]
    
    virustotal = False
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "virustotal_api.txt")
    
    if os.path.exists(file_path):
        virustotal = True
        with open(file_path, "r") as file:
            api_key = file.read().strip()
        print("[+] Finding Subdomains Using VirusTotal.")
        get_subdomains(target_dir, target, api_key)
    else:
        print("[-] VirusTotal Is Not Integrated.")

    if enable_bruteforce:
        brute_force_commands = [
            f"findomain -t {target} -w /usr/share/wordlists/SecLists/Discovery/DNS/n0kovo_subdomains.txt -o -v",
            f"mv {target}.txt {target_dir}/findomain-brute-{target}.txt",
        ]
        commands.extend(brute_force_commands)
    
    subdomains = f'{target_dir}/{target}_subdomains.txt' if virustotal else ''
    subdomains2 = f'{target_dir}/findomain-brute-{target}.txt' if enable_bruteforce else ''

    # Merge and sort subdomain files
    final_subdomains_file = f"{target_dir}/final-{target}-subdomains.txt"
    subdomain_list_file = f"{target_dir}/subdomains-list.txt"
    resolved_subdomains_file = f"{target_dir}/resolved-final-subdomains.txt"
    
    merge_and_sort_files(final_subdomains_file, subdomains, f"{target_dir}/sub-{target}.txt",
                          f"{target_dir}/asset-{target}.txt", f"{target_dir}/sub-find-{target}.txt",
                          f"{target_dir}/findomain-{target}.txt", subdomains2)
    
    merge_and_sort_files(subdomain_list_file, final_subdomains_file)

    commands.append(f"dnsx -l {subdomain_list_file} -o {resolved_subdomains_file}")
    
    # Remove unnecessary files
    safe_remove_files([subdomains, subdomain_list_file, f"{target_dir}/sub-{target}.txt", 
                       f"{target_dir}/asset-{target}.txt", f"{target_dir}/sub-find-{target}.txt", 
                       f"{target_dir}/findomain-{target}.txt", subdomains2, final_subdomains_file])

    run_section("Subdomain Enumeration, Discovery, Bruteforce, and Resolving", commands)
