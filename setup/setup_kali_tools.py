import os

def get_linux_distro():
    try:
        with open("/etc/os-release", "r") as f:
            data = f.read()
        if "Ubuntu" in data:
            return "Ubuntu"
        elif "Debian" in data:
            return "Debian"
        elif "Arch" in data:
            return "Arch"
        elif "Fedora" in data:
            return "Fedora"
        elif "openSUSE" in data:
            return "openSUSE"
        else:
            return "Unknown"
    except FileNotFoundError:
        return "Unknown"

def is_kali_repo_added():
    return os.path.exists("/etc/apt/sources.list.d/kali.list")

def add_kali_repo():
    print("Adding Kali Linux repository...")
    os.system("echo \"deb http://http.kali.org/kali kali-rolling main non-free contrib\" | sudo tee /etc/apt/sources.list.d/kali.list")
    
    print("Adding Kali Linux GPG key...")
    os.system("wget -qO - https://archive.kali.org/archive-key.asc | sudo tee /etc/apt/trusted.gpg.d/kali.asc")

def configure_apt_pinning():
    print("Configuring APT pinning to prevent conflicts...")
    pref_content = """Package: *\nPin: release a=kali-rolling\nPin-Priority: 100\n"""
    os.system("echo \"{}\" | sudo tee /etc/apt/preferences.d/kali.pref".format(pref_content))

def update_packages():
    print("Updating package list...")
    os.system("sudo apt update")

def setup():
    distro = get_linux_distro()
    if distro not in ["Ubuntu", "Debian"]:
        print("This script currently supports only Debian-based systems.")
        return
    
    if is_kali_repo_added():
        print("Kali repository is already configured on this system.")
    else:
        add_kali_repo()
        configure_apt_pinning()
        update_packages()
        print("\nSetup complete! You can now install Kali Linux tools using:\n")
        print("sudo apt -t kali-rolling install <tool-name>")
