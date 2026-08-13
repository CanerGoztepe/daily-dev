import sys
import os

def parse_env_file(filepath):
    keys = set()
    if not os.path.exists(filepath):
        return keys
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key = line.split('=', 1)[0].strip()
                keys.add(key)
    return keys

def audit_env(target, template):
    target_keys = parse_env_file(target)
    template_keys = parse_env_file(template)
    
    missing = template_keys - target_keys
    
    if not missing:
        print(f"Success: {target} is in sync with {template}.")
        return True
    
    print(f"Audit Failed: {target} is missing the following keys found in {template}:")
    for key in sorted(missing):
        print(f" - {key}")
    return False

def main():
    if len(sys.argv) != 3:
        print("Usage: python env_audit.py <target_env> <template_env>")
        sys.exit(1)
    
    target_file, template_file = sys.argv[1], sys.argv[2]
    
    if not os.path.exists(template_file):
        print(f"Error: Template file '{template_file}' not found.")
        sys.exit(1)
        
    if not audit_env(target_file, template_file):
        sys.exit(1)

if __name__ == '__main__':
    main()
