import os
from colorama import Fore, Style, init
init(autoreset=True)
def delete_empty_text_files(folder_path):
    try:
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path) and filename.endswith(".txt"):
                if os.path.getsize(file_path) == 0:
                    print(f"{Fore.RED}Deleting empty file: {filename}")
                    os.remove(file_path)
                else:
                    print(f"{Fore.GREEN}File is not empty: {filename}")
    except Exception as e:
        print(f"An error occurred: {e}")
