import os
import time
import sys

def cleanup_stale_files(directory, days_old):
    seconds_threshold = days_old * 86400
    now = time.time()
    deleted_count = 0
    errors = 0

    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory.")
        return

    print(f"Scanning {directory} for files older than {days_old} days...")

    for root, dirs, files in os.walk(directory):
        for name in files:
            file_path = os.path.join(root, name)
            try:
                file_age = os.path.getmtime(file_path)
                if (now - file_age) > seconds_threshold:
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                    deleted_count += 1
            except (OSError, PermissionError) as e:
                print(f"Could not process {file_path}: {e}")
                errors += 1

    print(f"Cleanup complete. Deleted: {deleted_count} files. Errors encountered: {errors}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python cleanup.py <directory_path> <days_threshold>")
    else:
        target_dir = sys.argv[1]
        try:
            threshold = int(sys.argv[2])
            cleanup_stale_files(target_dir, threshold)
        except ValueError:
            print("Error: Days threshold must be an integer.")
