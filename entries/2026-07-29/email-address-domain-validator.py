import re

def validate_emails(emails, allowed_domains):
    """Validates email syntax and domain authorization."""
    # Regex for standard RFC 5322 compliant email format
    email_pattern = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    results = {"valid": [], "invalid": []}
    
    # Normalize domains to lowercase for case-insensitive matching
    allowed = {d.lower() for d in allowed_domains}
    
    for email in emails:
        try:
            # Ensure input is string
            email_str = str(email).strip()
            
            # Validate syntax
            if not email_pattern.match(email_str):
                results["invalid"].append(email_str)
                continue
            
            # Validate domain existence
            _, domain = email_str.rsplit('@', 1)
            if domain.lower() in allowed:
                results["valid"].append(email_str)
            else:
                results["invalid"].append(email_str)
        except (ValueError, AttributeError):
            results["invalid"].append(email)
            
    return results

def main():
    raw_input = ["alice@company.com", "bob@external.org", "bad_email.com", "charlie@company.com"]
    trusted_domains = ["company.com", "internal.net"]
    
    validation_report = validate_emails(raw_input, trusted_domains)
    
    print(f"Processing complete.")
    print(f"Authorized: {validation_report['valid']}")
    print(f"Rejected/Invalid: {validation_report['invalid']}")

if __name__ == "__main__":
    main()
