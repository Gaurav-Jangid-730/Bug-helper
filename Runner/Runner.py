import subprocess
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, Style, init

init(autoreset=True)

def run_command(commands):
    for command in commands:
        try:
            print(f"{Fore.CYAN}{'-'*80}\n{Fore.GREEN}Running: {Fore.WHITE}{command}\n{'-'*80}")
            process = subprocess.Popen(command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            for line in process.stdout:
                print(line, end="")
            process.stdout.close()
            return_code = process.wait()
            if return_code != 0:
                print(f"Command failed with error code: {return_code}")
                for line in process.stderr:
                    print(line, end="")
        except Exception as e:
            print(f"{Fore.RED}An error occurred while running: {command}")
            print(f"{Fore.RED}{e}")

def run_section(section_name, commands):
    print(f"\n{Fore.MAGENTA}{'='*80}\nStarting Section: {section_name}\n{'='*80}")
    run_command(commands)
    print(f"\n{Fore.MAGENTA}{'='*80}\nCompleted Section: {section_name}\n{'='*80}")