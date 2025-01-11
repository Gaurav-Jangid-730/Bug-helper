import re
import os

def load_file_lines(file_path):
    """
    Reads all non-empty lines from a file and returns them as a list.
    """
    try:
        with open(file_path, 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"[ERROR] The file {file_path} was not found.")
        return []
    except Exception as e:
        print(f"[ERROR] An error occurred while reading the file: {e}")
        return []

def convert_wildcard_to_regex(pattern):
    """
    Converts a wildcard pattern (e.g., *.example.com) into a regex pattern.
    """
    return re.escape(pattern).replace(r'\*', '.*')

def filter_subdomains(subdomains, out_of_scope_patterns):
    """
    Filters subdomains by removing those that match any out-of-scope pattern.
    """
    filtered_subdomains = []
    compiled_patterns = [re.compile(convert_wildcard_to_regex(pattern)) for pattern in out_of_scope_patterns]

    for subdomain in subdomains:
        if any(pattern.match(subdomain) for pattern in compiled_patterns):
            print(f"[INFO] Excluding out-of-scope subdomain: {subdomain}")
        else:
            filtered_subdomains.append(subdomain)
    
    return filtered_subdomains

def main():
    # Step 1: Get input file paths from the user
    subdomains_file = input("[INFO] Enter the path to the subdomains file: ").strip()
    out_of_scope_file = input("[INFO] Enter the path to the out-of-scope file: ").strip()

    if not os.path.exists(subdomains_file) or not os.path.exists(out_of_scope_file):
        print("[ERROR] One or both files do not exist. Please check the paths.")
        return

    # Step 2: Load subdomains and out-of-scope patterns
    subdomains = load_file_lines(subdomains_file)
    out_of_scope_patterns = load_file_lines(out_of_scope_file)

    if not subdomains:
        print("[ERROR] No subdomains found in the input file.")
        return

    if not out_of_scope_patterns:
        print("[INFO] No out-of-scope patterns provided. No filtering will be performed.")
        return

    # Step 3: Filter subdomains
    filtered_subdomains = filter_subdomains(subdomains, out_of_scope_patterns)

    # Step 4: Save filtered subdomains to a new file
    output_file = os.path.join(os.path.dirname(subdomains_file), "filtered-subdomains.txt")
    try:
        with open(output_file, 'w') as file:
            file.write("\n".join(filtered_subdomains))
        print(f"[INFO] Filtered subdomains saved to: {output_file}")
    except Exception as e:
        print(f"[ERROR] An error occurred while writing to the file: {e}")

if __name__ == "__main__":
    main()
