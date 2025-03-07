#!/usr/bin/env python3

import os
import shutil
import subprocess
from Runner.Runner import run_command

# Get the current script directory (tool's root directory)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOOL_NAME = os.path.basename(SCRIPT_DIR)  # Tool folder name
DEST_PATH = os.path.join("/opt", TOOL_NAME)
EXECUTABLE_NAME = "bug-helper"
EXECUTABLE_PATH = os.path.join(DEST_PATH, EXECUTABLE_NAME + ".py")
LINK_PATH = f"/usr/local/bin/{EXECUTABLE_NAME}"
WRAPPER_SCRIPT = f"/usr/local/bin/{EXECUTABLE_NAME}"

commands = [
    "apt install unzip",
    "apt install golang-go",
    "export PATH=$PATH:$(go env GOPATH)/bin",
    "apt install pipx",
    "sudo apt install python3-colorama python3-requests python3-dnspython python3-urllib3 python3-bs4 python3-idna python3-prompt-toolkit python3-tldextract"
]

def copy_tool():
    """Copy the tool folder to /opt/"""
    if os.path.exists(DEST_PATH):
        print(f"Removing existing tool folder in {DEST_PATH}...")
        shutil.rmtree(DEST_PATH)

    print(f"Copying {SCRIPT_DIR} to {DEST_PATH}...")
    shutil.copytree(SCRIPT_DIR, DEST_PATH)
    os.chmod(DEST_PATH, 0o755)

def create_wrapper_script():
    """Create a wrapper script to ensure Python executes bug-helper"""
    wrapper_content = f"""#!/bin/bash
python3 "{EXECUTABLE_PATH}" "$@"
"""
    with open(WRAPPER_SCRIPT, "w") as f:
        f.write(wrapper_content)

    subprocess.run(["chmod", "+x", WRAPPER_SCRIPT], check=True)

def main():
    if not os.path.exists(SCRIPT_DIR):
        print(f"Error: {SCRIPT_DIR} not found!")
        return

    copy_tool()
    create_wrapper_script()
    run_command(commands)
    
    print("\nSetup complete! You can now run your tool using:")
    print(f"    {EXECUTABLE_NAME}")

if __name__ == "__main__":
    main()
