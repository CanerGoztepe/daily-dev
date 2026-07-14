import sys
import re
from collections import Counter

def analyze_logs(file_path):
    level_counts = Counter()
    error_messages = Counter()
    # Pattern assumes standard log format: YYYY-MM-DD HH:MM:SS [LEVEL] Message
    log_pattern = re.compile(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \[(.*?)\] (.*)')

    try:
        with open(file_path, 'r') as file:
            for line in file:
                match = log_pattern.search(line)
                if match:
                    level, message = match.groups()
                    level_counts[level] += 1
                    if level in ['ERROR', 'CRITICAL']:
                        error_messages[message.strip()] += 1
    except FileNotFoundError:
        print(f'Error: File {file_path} not found.')
        return
    except Exception as e:
        print(f'An error occurred: {e}')
        return

    print('--- Log Level Summary ---')
    for level, count in level_counts.items():
        print(f'{level}: {count}')

    print('\n--- Top 5 Error Messages ---')
    for msg, count in error_messages.most_common(5):
        print(f'{count}x: {msg}')

def main():
    if len(sys.argv) < 2:
        print('Usage: python log_analyzer.py <path_to_log_file>')
        sys.exit(1)
    analyze_logs(sys.argv[1])

if __name__ == '__main__':
    main()
