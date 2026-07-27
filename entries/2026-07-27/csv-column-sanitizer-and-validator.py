import csv
import sys
import os

def sanitize_csv(input_path, output_path, required_columns=None):
    if not os.path.exists(input_path):
        print(f"Error: File {input_path} not found.")
        return

    try:
        with open(input_path, mode='r', encoding='utf-8', newline='') as infile:
            reader = csv.DictReader(infile)
            headers = [h.strip() for h in reader.fieldnames]
            
            with open(output_path, mode='w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=headers)
                writer.writeheader()
                
                for row_idx, row in enumerate(reader, start=2):
                    cleaned_row = {k.strip(): (v.strip() if v else '') for k, v in row.items()}
                    
                    # Validation check
                    if required_columns:
                        for col in required_columns:
                            if col not in cleaned_row or not cleaned_row[col]:
                                print(f"Skipping row {row_idx}: Missing value in required column '{col}'")
                                continue
                    
                    writer.writerow(cleaned_row)
        print(f"Successfully processed CSV to {output_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    if len(sys.argv) < 3:
        print("Usage: python script.py <input_csv> <output_csv>")
        sys.exit(1)
    
    # Example: Ensuring 'ID' and 'Email' columns are present and populated
    sanitize_csv(sys.argv[1], sys.argv[2], required_columns=['ID', 'Email'])

if __name__ == '__main__':
    main()
