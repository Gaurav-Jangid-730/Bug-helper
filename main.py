import os
import argparse
from setup.setup_dir import setup_directories
from setup.remove_file import delete_empty_text_files
from subdomain_Enumatration.subdomain_finder import subdomain_finding
from setup.check_dependency import check_dependencies
from DNS_Enumration.DNS_Checker import dns_enum
from URL_Extractor.url_finder import Url_finding
from XSS_scanner.xss_scanning import xss_scanning

def parse_arguments():
    parser = argparse.ArgumentParser(description="Automate bug bounty process.")
    parser.add_argument("-d", "--domain", help="Specify the domain name", required=False)
    return parser.parse_args()

args = parse_arguments()
target = args.domain if args.domain else os.getenv("target")

if not target:
    print("Error: No target domain provided.")
    exit(1)
    
if __name__ == "__main__":
    check_dependencies()
    args = parse_arguments()
    target = args.domain if args.domain else os.getenv("target")

    if not target:
        print("Error: No target domain provided.")
        exit(1)
    target_dir = setup_directories(target)
    subdomain_finding(target, target_dir)
    dns_enum(target_dir)
    delete_empty_text_files(f"{target_dir}/DNS")
    Url_finding(target,target_dir)
    xss_scanning(target_dir)
    print(f"All tasks completed. Check the results in {target_dir}")