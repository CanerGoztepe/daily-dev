import sys
import re
from collections import defaultdict
from datetime import datetime

def analyze_bursts(file_path, window_size, threshold):
    # Assumes standard log format with timestamp at the start: YYYY-MM-DD HH:MM:SS
    ts_pattern = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})')
    counts = defaultdict(int)
    
    try:
        with open(file_path, 'r') as f:
            for line in f:
                match = ts_pattern.match(line)
                if match:
                    dt = datetime.strptime(match.group(1), '%Y-%m-%d %H:%M:%S')
                    # Normalize to the window start time
                    ts_key = (int(dt.timestamp()) // window_size) * window_size
                    counts[ts_key] += 1
        
        print(f"Analyzing bursts (window: {window_size}s, threshold: {threshold}):")
        found = False
        for ts, count in sorted(counts.items()):
            if count > threshold:
                start_time = datetime.fromtimestamp(ts)
                print(f"Burst detected at {start_time}: {count} logs (Limit: {threshold})")
                found = True
        
        if not found:
            print("No bursts detected within the specified threshold.")
            
    except FileNotFoundError:
        print("Error: File not found.")
    except ValueError:
        print("Error: Invalid date format in log file.")

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python script.py <file> <window> <threshold>")
    else:
        try:
            path = sys.argv[1]
            win = int(sys.argv[2])
            limit = int(sys.argv[3])
            analyze_bursts(path, win, limit)
        except ValueError:
            print("Error: Window and threshold must be integers.")
