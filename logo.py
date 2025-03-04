import os
from colorama import Fore, init

init(autoreset=True)

def display_logo():
    logo = f"""{Fore.RED}
        ██████╗ ██╗   ██╗ ██████╗       ██╗  ██╗███████╗██╗     ██████╗ ███████╗██████╗ 
        ██╔══██╗██║   ██║██╔════╝       ██║  ██║██╔════╝██║     ██╔══██╗██╔════╝██╔══██╗
        ██████╔╝██║   ██║██║  ███╗█████╗███████║█████╗  ██║     ██████╔╝█████╗  ██████╔╝
        ██╔══██╗██║   ██║██║   ██║╚════╝██╔══██║██╔══╝  ██║     ██╔═══╝ ██╔══╝  ██╔══██╗
        ██████╔╝╚██████╔╝╚██████╔╝      ██║  ██║███████╗███████╗██║     ███████╗██║  ██║
        ╚═════╝  ╚═════╝  ╚═════╝       ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝     ╚══════╝╚═╝  ╚═╝
                                                            ~ CREATED BY : GAURAV SHARMA
        """
    os.system('cls' if os.name == 'nt' else 'clear')
    print(logo)