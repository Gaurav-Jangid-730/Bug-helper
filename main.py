import os
from setup.setup_dir import setup_directories
from setup.remove_file import delete_empty_text_files
from subdomain_Enumatration.subdomain_finder import subdomain_finding
from setup.check_dependency import install_tools
from setup.setup_kali_tools import setup
from DNS_Enumration.DNS_Checker import dns_enum
from URL_Extractor.url_finder import Url_finding
from XSS_scanner.xss_scanning import xss_scanning
from colorama import Fore, init

init(autoreset=True)

def display_logo():
    logo = f"""{Fore.RED}
        ██████╗ ██╗   ██╗ ██████╗       ██╗  ██╗███████╗██╗     ██████╗ ███████╗██████╗ 
        ██╔══██╗██║   ██║██╔════╝       ██║  ██║██╔════╝██║     ██╔══██╗██╔════╝██╔══██╗
        ██████╔╝██║   ██║██║  ███╗█████╗███████║█████╗  ██║     ██████╔╝█████╗  ██████╔╝
        ██╔══██╗██║   ██║██║   ██║╚════╝██╔══██║██╔══╝  ██║     ██╔═══╝ ██╔══╝  ██╔══██╗
        ██████╔╝╚██████╔╝╚██████╔╝      ██║  ██║███████╗███████╗██║     ███████╗██║  ██║
        ╚═════╝  ╚═════╝  ╚═════╝       ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝
"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print(logo)

def select_target():
    print(f"{Fore.YELLOW}\nSelect Target Input Method:")
    print(f"{Fore.YELLOW}1. Use Target From Environment Variable")
    print(f"{Fore.YELLOW}2. Enter Target Manually")
    choice = input("Enter choice (1/2): ")
    os.system('cls' if os.name == 'nt' else 'clear')
    display_logo()
    if choice == "1":
        return os.getenv("target")
    elif choice == "2":
        return input(f"{Fore.YELLOW}Enter the target domain: ")
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

def execute_functions(selected_functions, target, target_dir):
    functions = {
        1: lambda: subdomain_finding(target, target_dir),
        2: lambda: dns_enum(target_dir),
        3: lambda: delete_empty_text_files(f"{target_dir}/DNS"),
        4: lambda: Url_finding(target, target_dir),
        5: lambda: xss_scanning(target_dir)
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
    display_logo()
    setup()
    install_tools()
    target = select_target()
    if not target:
        print(f"{Fore.RED}Error: No target domain provided.")
        exit(1)
    
    print(f"{Fore.WHITE}\nSetup in progress...\n")
    target_dir = setup_directories(target)
    
    print(f"{Fore.YELLOW}\nSelect Functions to Run:")
    print("0 - Run all functions in order")
    print("1 - Subdomain Enumeration")
    print("2 - DNS Enumeration")
    print("3 - Remove Empty Files")
    print("4 - URL Extraction")
    print("5 - XSS Scanning")
    
    selected_input = input(f"{Fore.YELLOW}Enter function numbers (e.g., 1-2 3 6): ")
    os.system('cls' if os.name == 'nt' else 'clear')
    display_logo()
    selected_functions = parse_function_selection(selected_input)

    execute_functions(selected_functions, target, target_dir)
    
    print(f"{Fore.GREEN}\nAll tasks completed. Check the results in {target_dir}")
