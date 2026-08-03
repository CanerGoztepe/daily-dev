import os
import shutil
import sys
from pathlib import Path

def organize_directory(target_dir):
    path = Path(target_dir)
    if not path.exists() or not path.is_dir():
        print(f"Error: {target_dir} is not a valid directory.")
        return

    print(f"Organizing files in: {path.absolute()}")
    
    for item in path.iterdir():
        if item.is_file():
            # Skip files without extensions or hidden files
            if not item.suffix:
                continue
            
            # Extract extension and clean leading dot
            ext = item.suffix.lower()[1:]
            dest_folder = path / ext
            
            try:
                dest_folder.mkdir(exist_ok=True)
                shutil.move(str(item), str(dest_folder / item.name))
                print(f"Moved: {item.name} -> {ext}/")
            except Exception as e:
                print(f"Failed to move {item.name}: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python organize.py <directory_path>")
        return
    
    target = sys.argv[1]
    confirm = input(f"Organize files in '{target}' by extension? (y/n): ")
    if confirm.lower() == 'y':
        organize_directory(target)
    else:
        print("Operation cancelled.")

if __name__ == "__main__":
    main()
