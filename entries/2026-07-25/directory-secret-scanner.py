import os
import re
import sys

# Patterns to match potential secrets
PATTERNS = {
    'Generic API Key': r'(?i)(api_key|apikey|secret|token)[:\s"\']{1,3}([a-zA-Z0-9]{20,})',
    'Private Key': r'-----BEGIN (RSA|DSA|EC|OPENSSH) PRIVATE KEY-----'
}

def scan_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                for label, pattern in PATTERNS.items():
                    if re.search(pattern, line):
                        print(f'[!] Found {label} in {filepath}:{line_num}')
    except Exception as e:
        print(f'[E] Could not read {filepath}: {e}')

def main():
    if len(sys.argv) < 2:
        print('Usage: python scanner.py <directory>')
        sys.exit(1)

    target_dir = sys.argv[1]
    if not os.path.isdir(target_dir):
        print(f'Error: {target_dir} is not a valid directory')
        sys.exit(1)

    print(f'Scanning directory: {target_dir} ...')
    for root, _, files in os.walk(target_dir):
        for file in files:
            # Skip common non-source directories
            if '.git' in root or '__pycache__' in root:
                continue
            scan_file(os.path.join(root, file))
    print('Scan complete.')

if __name__ == '__main__':
    main()
