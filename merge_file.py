def merge_and_sort_files(file1, file2, output_file):
    # Read content from the first file
    with open(file1, 'r', encoding='utf-8') as f1:
        lines1 = set(f1.read().splitlines())
    
    # Read content from the second file
    with open(file2, 'r', encoding='utf-8') as f2:
        lines2 = set(f2.read().splitlines())
    
    # Merge and remove duplicates
    merged_lines = lines1 | lines2
    
    # Sort by line length
    sorted_lines = sorted(merged_lines, key=len)
    
    # Count new lines added to file1
    new_lines_added = len(merged_lines) - len(lines1)
    
    # Write to the output file
    with open(output_file, 'w', encoding='utf-8') as out:
        for line in sorted_lines:
            out.write(line + '\n')
    
    print(f"New lines added from {file2} to {file1}: {new_lines_added}")
    print(f"Merged content saved to {output_file}")

# Example usage
file1 = r"C:\Users\Gaurav.Googlly\Desktop\Projects\python_Projects\Bug-finding-helper\Open_redirect\payloads.txt"
file2 = r"C:\Users\Gaurav.Googlly\Desktop\Open-Redirect-payloads.txt"
output_file = r"C:\Users\Gaurav.Googlly\Desktop\Projects\python_Projects\Bug-finding-helper\Open_redirect\payloads2.txt"
merge_and_sort_files(file1, file2, output_file)