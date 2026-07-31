import csv
import hashlib
import os

def anonymize_csv(input_file, output_file, target_columns, salt='SECRET_SALT'):
    """Reads a CSV, hashes specified columns, and writes to a new file."""
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file {input_file} not found.")

    try:
        with open(input_file, mode='r', encoding='utf-8', newline='') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames
            
            if not all(col in fieldnames for col in target_columns):
                missing = [c for c in target_columns if c not in fieldnames]
                raise ValueError(f"Columns not found in CSV: {missing}")

            with open(output_file, mode='w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()

                for row in reader:
                    for col in target_columns:
                        # Create a consistent hash of the sensitive value
                        raw_val = f"{row[col]}{salt}".encode('utf-8')
                        row[col] = hashlib.sha256(raw_val).hexdigest()[:12]
                    writer.writerow(row)
    except Exception as e:
        print(f"An error occurred during processing: {e}")

if __name__ == '__main__':
    # Example: Masking 'email' and 'phone' columns
    # Input CSV format: name,email,phone,city
    input_csv = 'users.csv'
    output_csv = 'users_anonymized.csv'
    cols_to_mask = ['email', 'phone']
    
    # anonymize_csv(input_csv, output_csv, cols_to_mask)
    print("Utility ready for use. Ensure input file exists before running.")
