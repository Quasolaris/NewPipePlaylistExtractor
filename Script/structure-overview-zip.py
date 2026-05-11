#!/usr/bin/env python3

# structure-overview-zip.py
#
# It reads the ZIP file
# extracts the internal folder/file structure
# writes a human-readable, tree-style structure overview
#
# Usage Example:
# python3 structure-overview-zip.py archive.zip structure-overview.txt
#
# - The first argument is the input ZIP archive.
# - The second argument is the output structure-overview.txt

import sys
import zipfile
from collections import defaultdict

def build_tree(paths):
    """
    Build a nested dictionary tree from list of zip paths
    """
    tree = lambda: defaultdict(tree)
    root = tree()
    for path in paths:
        parts = path.rstrip('/').split('/')
        current = root
        for part in parts:
            current = current[part]
    return root

def print_tree(d, indent=0, is_last=True, prefix=''):
    """
    Print the directory tree in a tree-like format.
    """
    lines = []
    keys = list(d.keys())
    for i, key in enumerate(keys):
        last = (i == len(keys) - 1)
        branch = '└── ' if last else '├── '
        line = prefix + branch + key
        if d[key]:
            line += '/'
        lines.append(line)
        extension = '    ' if last else '│   '
        if d[key]:
            lines.extend(print_tree(d[key], indent + 1, last, prefix + extension))
    return lines

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 structure-overview-zip.py archive.zip structure-overview.txt")
        sys.exit(1)

    zip_filename = sys.argv[1]
    output_file = sys.argv[2]

    with zipfile.ZipFile(zip_filename, 'r') as zipf:
        paths = zipf.namelist()

    tree = build_tree(paths)

    lines = [f"{zip_filename}"]
    lines.append('│')
    lines.extend(print_tree(tree))

    with open(output_file, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")

    print(f"Structure overview saved to {output_file}")

if __name__ == "__main__":
    main()
