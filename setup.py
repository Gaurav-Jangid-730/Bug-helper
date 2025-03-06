from setuptools import setup, find_packages
import os
import stat

TOOL_NAME = "bug-helper"
MAIN_SCRIPT = "main.py"

# Create an executable shell script for Unix-like systems
executable_script = f"""#!/bin/bash
python3 {os.path.abspath(MAIN_SCRIPT)} "$@"
"""

# Write the shell script to /usr/local/bin or ~/.local/bin
bin_path = f"/usr/local/bin/{TOOL_NAME}"
try:
    with open(bin_path, "w") as f:
        f.write(executable_script)
    os.chmod(bin_path, os.stat(bin_path).st_mode | stat.S_IEXEC)
    print(f"Executable {TOOL_NAME} created at {bin_path}")
except PermissionError:
    print(f"Permission denied! Try running with sudo: sudo python3 setup.py install")

# Setup script
setup(
    name=TOOL_NAME,
    version="1.0.0",
    packages=find_packages(),
    py_modules=["main"],  # Ensure main.py exists
    install_requires=[],  # Add dependencies if needed
    entry_points={
        "console_scripts": [
            f"{TOOL_NAME}=main:main",  # Ensure main.py has a main() function
        ],
    },
)
