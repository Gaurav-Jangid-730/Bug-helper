import os
from colorama import Fore, Style, init

init(autoreset=True)

def read_domain_ip_mapping(file_path):
    domain_ip_map = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                parts = line.strip().split()
                if len(parts) == 2:
                    domain, ip = parts
                    domain_ip_map[domain] = ip
    except FileNotFoundError:
        print(f"{Fore.RED}[ERROR] The file {file_path} was not found.")
    except Exception as e:
        print(f"{Fore.RED}[ERROR] An error occurred while reading the file: {e}")
    
    return domain_ip_map

def ip_placer(target , target_dir):
    # Ask the user for the domain-IP mapping file
    file_path = input(f"{Fore.YELLOW}[INFO] Enter the path to the domain-IP mapping file (leave empty if none): ").strip()
    # Load domain-IP mappings if the file exists and is provided
    domain_ip_map = {}
    if file_path:
        if os.path.exists(file_path):
            domain_ip_map = read_domain_ip_mapping(file_path)
            if not domain_ip_map:
                print(f"{Fore.YELLOW}[INFO] No valid domain-IP mappings found in the file.")
        else:
            print(f"{Fore.RED}[ERROR] The file at {file_path} does not exist. Proceeding without domain-IP replacements.")
    file = f'URL_FOR_{target}.txt'
    # Path to the input file containing subdomains to process
    input_file_path = os.path.join(target_dir,file)
    if not os.path.exists(input_file_path):
        print(f"{Fore.RED}[ERROR] The input file {input_file_path} does not exist.")
        return

    # Open the input file and prepare the output file
    processed_file_path = os.path.join(target_dir, "processed-urls.txt")
    
    if file_path:
        with open(input_file_path, "r") as infile, open(processed_file_path, "w") as outfile:
            for url in infile:
                original_url = url.strip()
                modified_url = original_url

                # Replace the domain with the corresponding IP address
                for domain, ip in domain_ip_map.items():
                    if domain in modified_url:
                        modified_url = modified_url.replace(domain, ip)
                        print(f"{Fore.YELLOW}[INFO] Replacing {domain} with IP: {ip} in URL: {original_url}")

                # Write the modified URL to the processed file
                outfile.write(modified_url + "\n")
        print(f"{Fore.YELLOW}[INFO] Process completed. The replaced URLs are saved in: {processed_file_path}")