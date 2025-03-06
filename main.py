import os
from Path import interactive_UI
from logo import display_logo
from Start_up.setup_dir import setup_directories
from subdomain_Enumatration.subdomain_finder import subdomain_finding
from Start_up.check_dependency import install_tools
from Start_up.setup_kali_tools import setup
from Subdomain_takeover.subdomain_takeover import subdomain_takeover
from Open_redirect.Open_redirect import open_redirect
from DNS_Enumration.DNS_Transfer import DNS_transfer
from URL_Extractor.url_finder import Url_finding
from XSS_scanner.xss_scanning import xss_scanning
from colorama import Fore, init

init(autoreset=True)

def check_for_updates():
    repo_url = "https://github.com/your-username/Bug-helper.git"  # Replace with actual repo URL
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    
    if not os.path.exists(os.path.join(repo_dir, ".git")):
        print(f"{Fore.RED}Git repository not found. Make sure the tool is cloned from GitHub.")
        return
    
    print(f"{Fore.YELLOW}Checking for updates...")
    subprocess.run(["git", "fetch"], cwd=repo_dir)
    status = subprocess.run(["git", "status", "-uno"], capture_output=True, text=True, cwd=repo_dir)
    
    if "Your branch is behind" in status.stdout:
        print(f"{Fore.GREEN}Update available! Pulling latest changes...")
        subprocess.run(["git", "pull"], cwd=repo_dir)
        print(f"{Fore.GREEN}Update completed. Restart the tool to apply changes.")
        exit(0)
    else:
        print(f"{Fore.GREEN}Your tool is up to date.")

def get_target_list():
    print(f"{Fore.YELLOW}\nChoose Target Mode:")
    print(f"{Fore.YELLOW}1. Single Target")
    print(f"{Fore.YELLOW}2. Multiple Targets (from file)")
    choice = input("Enter choice (1/2): ")
    os.system('cls' if os.name == 'nt' else 'clear')
    display_logo()
    
    if choice == "1":
        return [input(f"{Fore.YELLOW}Enter the target domain: ")]
    elif choice == "2":
        file_path = interactive_UI()
        if not os.path.exists(file_path):
            print(f"{Fore.RED}Error: File not found.")
            exit(1)
        with open(file_path, "r") as f:
            return [line.strip() for line in f if line.strip()]
    else:
        print(f"{Fore.RED}Invalid choice. Exiting.")
        exit(1)

def parse_function_selection(selection):
    selected_functions = set()
    parts = selection.replace(",", " ").split()
    
    for part in parts:
        if "-" in part:
            try:
                start, end = map(int, part.split("-"))
                selected_functions.update(range(start, end + 1))
            except ValueError:
                print(f"{Fore.RED}Invalid range: {part}")
        else:
            try:
                selected_functions.add(int(part))
            except ValueError:
                print(f"{Fore.RED}Invalid selection: {part}")
    
    return selected_functions

def execute_functions(selected_functions, target, target_dir, enable_bruteforce):
    functions = {
        1: lambda: subdomain_finding(target, target_dir, enable_bruteforce),
        2: lambda: DNS_transfer(target_dir),
        3: lambda: subdomain_takeover(target_dir, f'{target_dir}/resolved-final-subdomains.txt'),
        4: lambda: Url_finding(target, target_dir),
        5: lambda: open_redirect(target_dir, target),
        6: lambda: xss_scanning(target_dir)
    }
    
    if 0 in selected_functions:
        print(f"{Fore.YELLOW}\nRunning all functions in order...\n")
        for func in functions.values():
            func()
    else:
        for num in selected_functions:
            if num in functions:
                print(f"{Fore.YELLOW}Running function {num}...")
                functions[num]()
            else:
                print(f"{Fore.RED}Invalid function number: {num}")

if __name__ == "__main__":
    if len(os.sys.argv) > 1 and os.sys.argv[1] == "--up":
        check_for_updates()
    display_logo()
    setup()
    install_tools()
    targets = get_target_list()
    
    print(f"{Fore.YELLOW}\nSelect Functions to Run:")
    print("0 - Run all functions in order")
    print("1 - Subdomain Enumeration")
    print("2 - DNS Zone Transfer")
    print("3 - Performing Subdomain Takeover")
    print("4 - URL Extraction")
    print("5 - Open Redirection Bug")
    print("6 - XSS Scanning")
    
    selected_input = input(f"{Fore.YELLOW}Enter function numbers (e.g., 1-2 3 6): ")
    os.system('cls' if os.name == 'nt' else 'clear')
    display_logo()
    
    print(f"{Fore.YELLOW}\nDo you want to enable brute force scanning?")
    print("1 - Yes")
    print("2 - No")
    bruteforce_choice = input(f"{Fore.YELLOW}Enter your choice (1/2): ")
    enable_bruteforce = bruteforce_choice == "1"
    selected_functions = parse_function_selection(selected_input)
    
    for target in targets:
        print(f"{Fore.WHITE}\nSetup in progress for {target}...\n")
        target_dir = setup_directories(target)
        execute_functions(selected_functions, target, target_dir, enable_bruteforce)
        print(f"{Fore.GREEN}\nAll tasks completed for {target}. Check the results in {target_dir}")
