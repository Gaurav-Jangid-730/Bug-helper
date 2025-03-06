import os
import sys
import curses
import re
from logo import display_logo  # Import the logo function

# Determine starting directory
if sys.platform == "win32":
    START_DIR = "C:\\"
else:
    START_DIR = os.path.expanduser("~")  # Home directory in Linux/macOS

# Use readline on Linux/macOS, prompt_toolkit on Windows
if sys.platform == "win32":
    from prompt_toolkit import prompt
    from prompt_toolkit.completion import PathCompleter
    def get_user_input():
        """Get user input with path autocompletion (Windows)."""
        completer = PathCompleter()
        return prompt("📌 Enter path: ", completer=completer).strip()
else:
    import readline
    def complete_path(text, state):
        """Autocompletion for paths on Linux/macOS."""
        directory, partial = os.path.split(text)

        if not directory:
            directory = "."  # Use current directory if nothing is typed

        try:
            entries = os.listdir(directory)
        except FileNotFoundError:
            return None

        matches = [entry for entry in entries if entry.startswith(partial)]

        if state < len(matches):
            return os.path.join(directory, matches[state])
        return None

    def setup_autocomplete():
        """Setup the TAB autocompletion for paths (Linux/macOS)."""
        readline.set_completer(complete_path)
        readline.parse_and_bind("tab: complete")

    def get_user_input():
        """Get user input (Linux/macOS)."""
        return input("📌 Enter path (TAB for suggestions): ").strip()

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
    if sys.platform != "win32":
        setup_autocomplete()

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