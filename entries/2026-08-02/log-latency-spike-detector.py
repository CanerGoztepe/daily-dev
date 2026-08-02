import sys
from datetime import datetime

def analyze_log(file_path, threshold):
    """Parses log for timestamp gaps larger than threshold seconds."""
    prev_time = None
    try:
        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    # Assuming log format: YYYY-MM-DD HH:MM:SS
                    timestamp_str = line.split(',')[0].strip()
                    current_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    
                    if prev_time:
                        diff = (current_time - prev_time).total_seconds()
                        if diff > threshold:
                            print(f"Latency spike at line {line_num}: {diff}s gap detected.")
                    
                    prev_time = current_time
                except (ValueError, IndexError):
                    continue
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")

def main():
    if len(sys.argv) < 3:
        print("Usage: python log_analyzer.py <log_file> <seconds>")
        return
    
    path = sys.argv[1]
    try:
        limit = float(sys.argv[2])
        analyze_log(path, limit)
    except ValueError:
        print("Error: Threshold must be a number.")

if __name__ == '__main__':
    main()
