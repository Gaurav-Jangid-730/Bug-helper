import os
import sys
import curses
import re
from logo import display_logo  # Import the logo function

# Determine starting directory
START_DIR = "C:\\" if sys.platform == "win32" else os.path.expanduser("~")  # Home directory in Linux/macOS

# Import `prompt_toolkit` for path selection (Windows & Linux)
from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter
from prompt_toolkit.shortcuts import CompleteStyle

def get_user_input():
    """Get user input with path autocompletion (Windows & Linux)."""
    completer = PathCompleter(only_directories=False)
    return prompt(
        "📌 Enter path: ",
        completer=completer,
        complete_style=CompleteStyle.MULTI_COLUMN  # Scrollable & visually appealing
    ).strip()

def list_directory(path):
    """Return list of files and folders in the given path, including '..' for going back."""
    try:
        items = ["[BACK] .."]  # Add ".." to navigate up
        for item in sorted(os.listdir(path)):
            full_path = os.path.join(path, item.strip())
            if os.path.isdir(full_path):
                items.append(f"[DIR]  {item}")  # Mark folders
            else:
                items.append(f"[FILE] {item}")  # Mark files
        return items
    except PermissionError:
        return ["[Permission Denied]"]
    except FileNotFoundError:
        return ["[Invalid Path]"]

def interactive_path_selector(stdscr, base_path):
    """Interactive UI using curses for arrow key navigation, including 'Go Back (..)' option."""
    curses.curs_set(1)  # Show cursor
    current_index = 0
    path = base_path if os.path.isdir(base_path) else os.path.dirname(base_path)

    while True:
        stdscr.clear()
        display_logo()  # Display the logo on top
        stdscr.addstr(2, 0, f"📂 Browsing: {path}", curses.A_BOLD)

        items = list_directory(path)
        if not items:
            items = ["[Empty Directory]"]

        # Display items
        for idx, item in enumerate(items):
            prefix = "📁" if "[DIR]" in item else "📄" if "[FILE]" in item else "🔙"
            if idx == current_index:
                stdscr.addstr(idx + 4, 0, f"> {prefix} {item}", curses.A_REVERSE)
            else:
                stdscr.addstr(idx + 4, 0, f"  {prefix} {item}")

        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP and current_index > 0:
            current_index -= 1
        elif key == curses.KEY_DOWN and current_index < len(items) - 1:
            current_index += 1
        elif key == 10:  # Enter key
            selected = items[current_index]
            clean_selected = re.sub(r"^\[(DIR|FILE|BACK)\] ?", "", selected)

            new_path = os.path.normpath(os.path.join(path, clean_selected))

            if "[BACK]" in selected:
                path = os.path.dirname(path)
                current_index = 0
            elif "[DIR]" in selected:
                path = new_path
                current_index = 0
            elif "[FILE]" in selected:
                return new_path

def interactive_UI():
    """Main function for path selection."""
    while True:
        try:
            display_logo()  # Always display the logo on top
            print(f"\n📂 Default Start Directory: {START_DIR}\n")
            path = get_user_input() or START_DIR  # Start from home (Linux) or C:\ (Windows)

            if path.lower() == "exit":
                print("👋 Exiting tool.")
                break
            elif path.lower() == "browse":
                selected = curses.wrapper(interactive_path_selector, START_DIR)
                return selected if selected else None
            elif os.path.exists(path):
                print(f"\n📂 [Valid Path] {path}\n")
                return path
            else:
                print("❌ [Invalid Path] Try again.")
                return None
        except KeyboardInterrupt:
            print("\n👋 Exiting tool.")
            return None
