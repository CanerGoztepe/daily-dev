import os
import sys
from pathlib import Path

def validate_symlinks(root_dir):
    root = Path(root_dir)
    if not root.is_dir():
        print(f"Error: {root_dir} is not a valid directory.")
        return

    print(f"Scanning for broken symlinks in: {root}\n")
    broken_links = []

    try:
        for path in root.rglob('*'):
            if path.is_symlink():
                # resolve() will raise FileNotFoundError if the target doesn't exist
                try:
                    target = path.resolve(strict=True)
                except (FileNotFoundError, RuntimeError):
                    target = path.readlink()
                    broken_links.append((path, target))
                    print(f"[BROKEN] {path} -> {target}")

    except PermissionError:
        print("Error: Permission denied accessing some subdirectories.")

    if not broken_links:
        print("\nNo broken symbolic links found.")
    else:
        print(f"\nTotal broken links found: {len(broken_links)}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <directory_path>")
        sys.exit(1)
    
    target_dir = sys.argv[1]
    validate_symlinks(target_dir)

if __name__ == '__main__':
    main()
