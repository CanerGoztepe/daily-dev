import os
import shutil
import sys

# Supported extensions to check
VALID_EXTS = {'.jpg', '.png', '.mp3', '.pdf'}

def is_file_corrupt(filepath):
    """Checks if a file is readable by attempting to access a tiny header block."""
    try:
        with open(filepath, 'rb') as f:
            header = f.read(16)
            return len(header) < 16
    except (OSError, IOError):
        return True

def quarantine_files(source_dir, quarantine_dir):
    if not os.path.exists(quarantine_dir):
        os.makedirs(quarantine_dir)

    for root, _, files in os.walk(source_dir):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in VALID_EXTS:
                full_path = os.path.join(root, file)
                if is_file_corrupt(full_path):
                    dest_path = os.path.join(quarantine_dir, file)
                    print(f"Quarantining: {file}")
                    shutil.move(full_path, dest_path)

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <source_dir> <quarantine_dir>")
        sys.exit(1)

    src, dst = sys.argv[1], sys.argv[2]
    if not os.path.isdir(src):
        print("Error: Source directory does not exist.")
        sys.exit(1)

    print(f"Scanning {src} for corrupt files...")
    quarantine_files(src, dst)
    print("Scan complete.")

if __name__ == "__main__":
    main()
