import subprocess
from colorama import Fore, init

init(autoreset=True)

def is_tool_installed(tool):
    return subprocess.call(f"which {tool}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

def install_tools():
    tools = {
        "sublist3r": ["apt install sublist3r"],
        "assetfinder": ["go install github.com/tomnomnom/assetfinder@latest"],
        "subfinder": ["apt install subfinder"],
        "findomain": ["git clone https://github.com/Findomain/Findomain.git && cd Findomain && ./builder.sh"],
        "dnsx": ["GO111MODULE=on go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest"],
        "dnsrecon": ["pip install dnsrecon"],
        "cpulimit": ["sudo apt install cpulimit -y"],
        "katana": ["wget https://github.com/projectdiscovery/katana/releases/download/v1.1.0/katana_1.1.0_linux_amd64.zip",
                   "unzip katana_1.1.0_linux_amd64.zip",
                   "mv katana /usr/local/bin"],
        "waybackurls": ["go install github.com/tomnomnom/waybackurls@latest"],
        "waymore": ["pipx install git+https://github.com/xnl-h4ck3r/waymore.git"],
        "hakrawler": ["go install github.com/hakluke/hakrawler@latest"],
        "uro": ["pipx install uro"],
        "gf": ["go install github.com/tomnomnom/gf@latest",
               "cp /root/go/bin/gf /usr/local/bin",
               "mkdir ~/.gf",
               "cp ~/go/pkg/mod/github.com/tomnomnom/gf@v0.0.0-20200618134122-dcd4c361f9f5/examples/*.json ~/.gf",
               "git clone https://github.com/1ndianl33t/Gf-Patterns.git",
               "cp /Gf-Patterns/*.json ~/.gf"],
        "httpx": ["GO111MODULE=on go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest"],
        "qsreplace": ["go install github.com/tomnomnom/qsreplace@latest"],
        "airixss": ["go install github.com/ferreiraklet/airixss@latest"],
        "kxss": ["go install github.com/tomnomnom/hacks/kxss@latest"],
        "XSStrike": ["cd ~/tools",
                     "git clone https://github.com/s0md3v/XSStrike.git"]
    }
    
    for tool, commands in tools.items():
        if is_tool_installed(tool):
            print(f"{Fore.WHITE}[OK] {tool} is already installed.")
        else:
            print(f"{Fore.YELLOW}[INFO] Installing {tool}...")
            for command in commands:
                try:
                    subprocess.run(command, shell=True, check=True)
                    print(f"{Fore.GREEN}[SUCCESS] {tool} installed successfully.")
                    break
                except subprocess.CalledProcessError as e:
                    print(f"{Fore.RED}[ERROR] Failed to install {tool}. Error: {e}")

