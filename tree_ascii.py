#!/usr/bin/env python3
import os
import sys

def print_tree(root: str, prefix: str = "") -> None:
    try:
        entries = sorted(os.scandir(root), key=lambda e: (not e.is_dir(), e.name.lower()))
    except PermissionError:
        print(prefix + "[permission denied]")
        return

    entries = list(entries)
    for i, entry in enumerate(entries):
        is_last = (i == len(entries) - 1)
        branch = "└── " if is_last else "├── "
        print(prefix + branch + entry.name)

        if entry.is_dir(follow_symlinks=False):
            extension = "    " if is_last else "│   "
            print_tree(entry.path, prefix + extension)

def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    root = os.path.abspath(root)
    print(root)
    print_tree(root)

if __name__ == "__main__":
    main()
