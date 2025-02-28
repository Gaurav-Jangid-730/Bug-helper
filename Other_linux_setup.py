import os
import subprocess
from colorama import Fore, init

init(autoreset=True)

def run_command(command, check=True):
    """Run a shell command."""
    try:
        subprocess.run(command, shell=True, check=check, text=True)
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}Error while executing command: {command}\n{e}")
        exit(1)

def add_kali_repository():
    """Add Kali Linux repository to sources.list."""
    repo_entry = "deb http://http.kali.org/kali kali-rolling main non-free contrib\n"
    sources_list = "/etc/apt/sources.list"

    # Check if the repository is already added
    with open(sources_list, "r") as file:
        if repo_entry in file.read():
            print(f"{Fore.GREEN}Kali Linux repository is already added.")
            return

    # Add the repository
    print(f"{Fore.YELLOW}Adding Kali Linux repository...")
    with open(sources_list, "a") as file:
        file.write(repo_entry)
    print(f"{Fore.GREEN}Kali Linux repository added successfully.")

def add_kali_gpg_key():
    """Add Kali Linux GPG key."""
    print(f"{Fore.YELLOW}Adding Kali Linux GPG key...")
    command = "curl -fsSL https://archive.kali.org/archive-key.asc | gpg --dearmor -o /usr/share/keyrings/kali-archive-keyring.gpg"
    run_command(command)
    print(f"{Fore.GREEN}Kali Linux GPG key added successfully.")

def set_apt_pinning():
    """Set apt pinning to avoid conflicts between Ubuntu and Kali packages."""
    pinning_config = "/etc/apt/preferences.d/kali.pref"
    pinning_rules = """Package: *\nPin: release o=Kali\nPin-Priority: 100\n"""

    if os.path.exists(pinning_config):
        print(f"{Fore.GREEN}APT pinning for Kali is already configured.")
        return

    print(f"{Fore.YELLOW}Configuring APT pinning for Kali...")
    with open(pinning_config, "w") as file:
        file.write(pinning_rules)
    print(f"{Fore.GREEN}APT pinning configured successfully.")

def main():
    """Main function to execute all tasks."""
    if os.geteuid() != 0:
        print(f"{Fore.RED}This script must be run as root. Use 'sudo python3 script_name.py'.")
        exit(1)

    print(f"{Fore.YELLOW}Configuring This Linux for Kali Linux tools...")
    add_kali_repository()
    add_kali_gpg_key()
    set_apt_pinning()
    print(f"{Fore.GREEN}Now You Can Download Tools Like In Kali Linux")

if __name__ == "__main__":
    main()
