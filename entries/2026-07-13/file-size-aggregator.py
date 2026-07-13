import os
import sys
from pathlib import Path

def get_dir_size(path):
    """Calculate total size of a directory recursively."""
    total_size = 0
    try:
        for entry in os.scandir(path):
            if entry.is_file(follow_symlinks=False):
                total_size += entry.stat().st_size
            elif entry.is_dir(follow_symlinks=False):
                total_size += get_dir_size(entry.path)
    except PermissionError:
        pass
    return total_size

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <directory_path>")
        sys.exit(1)

    root_path = Path(sys.argv[1])
    if not root_path.is_dir():
        print(f"Error: {root_path} is not a valid directory.")
        sys.exit(1)

    print(f"Analyzing {root_path.resolve()}...\n")
    results = []

    try:
        for entry in os.scandir(root_path):
            if entry.is_dir():
                size = get_dir_size(entry.path)
                results.append((entry.name, size))
    except PermissionError:
        print("Error: Permission denied accessing target directory.")
        sys.exit(1)

    # Sort by size descending
    results.sort(key=lambda x: x[1], reverse=True)

    print(f"{'Directory Name':<30} | {'Size (MB)':<10}")
    print("-" * 45)
    for name, size in results:
        size_mb = size / (1024 * 1024)
        print(f"{name[:30]:<30} | {size_mb:>9.2f}")

if __name__ == "__main__":
    main()
