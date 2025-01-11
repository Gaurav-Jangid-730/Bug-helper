import subprocess
def check_dependencies():
    tools = ["sublist3r", "assetfinder", "subfinder"]
    for tool in tools:
        if subprocess.call(f"which {tool}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0:
            print(f"Error: {tool} is not installed. Please install it before running the script.")
            exit(1)
