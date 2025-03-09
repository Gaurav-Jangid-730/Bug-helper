import subprocess
import os
from logo import display_logo
from colorama import Fore, init

init(autoreset=True)

def is_tool_installed(tool, go_tool=False,path_check=False, pipx_check=False):
    if go_tool:
        return os.path.exists(os.path.expanduser(f"~/go/bin/{tool}"))
    if path_check:
        return os.path.exists(os.path.expanduser(f"~/tools/{tool}"))
    
    if pipx_check:
        result = subprocess.run(f"pipx list | grep {tool}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return tool in result.stdout  # Check if tool name appears in pipx list output

    return subprocess.call(f"which {tool}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

def install_tools():
    tools = {
        "sublist3r": ["apt install sublist3r -y"],
        "assetfinder": ["apt install assetfinder"],
        "subfinder": ["apt install subfinder -y"],
        "findomain": ["apt install findomain -y"],
        "dnsx": ["apt install dnsx -y"],
        "dnsrecon": ["apt install dnsrecon -y"],
        "cpulimit": ["sudo apt install cpulimit -y"],
        "katana": ["wget https://github.com/projectdiscovery/katana/releases/download/v1.1.0/katana_1.1.0_linux_amd64.zip && unzip katana_1.1.0_linux_amd64.zip && mv katana /usr/local/bin && rm katana_1.1.0_linux_amd64.zip"],
        "waybackurls": ["go install github.com/tomnomnom/waybackurls@latest"],
        "waymore": ["apt install waymore"],
        "hakrawler": ["go install github.com/hakluke/hakrawler@latest"],
        "uro": ["pipx install uro"],
        "gf": [
            "go install github.com/tomnomnom/gf@latest",
            "cp /root/go/bin/gf /usr/local/bin",
            "mkdir -p ~/.gf",
            "cp ~/go/pkg/mod/github.com/tomnomnom/gf@*/examples/*.json ~/.gf",
            "git clone https://github.com/1ndianl33t/Gf-Patterns.git",
            "cp Gf-Patterns/*.json ~/.gf"
        ],
        "httpx": ["GO111MODULE=on go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest"],
        "qsreplace": ["go install github.com/tomnomnom/qsreplace@latest"],
        "airixss": ["go install github.com/ferreiraklet/airixss@latest"],
        "kxss": ["go install github.com/tomnomnom/hacks/kxss@latest"],
        "XSStrike": ["mkdir -p ~/tools && cd ~/tools && git clone https://github.com/s0md3v/XSStrike.git"],
    }
    
    all_installed = True
    
    for tool, commands in tools.items():
        go_tool = any("go install" in cmd for cmd in commands)
        path_check = tool == "XSStrike"  # Check ~/tools for XSStrike
        pipx_check = tool in ["waymore", "uro"]  # Check pipx for these tools

        if is_tool_installed(tool, go_tool=go_tool, path_check=path_check, pipx_check=pipx_check):
            print(f"{Fore.GREEN}[OK] {tool} is already installed.")
        else:
            all_installed = False
            print(f"{Fore.YELLOW}[INFO] Installing {tool}...")
            for command in commands:
                try:
                    subprocess.run(command, shell=True, check=True)
                    print(f"{Fore.BLUE}[SUCCESS] {tool} installed successfully.")
                    break
                except subprocess.CalledProcessError as e:
                    print(f"{Fore.RED}[ERROR] Failed to install {tool}. Error: {e}")
    
    if all_installed:
        display_logo()
