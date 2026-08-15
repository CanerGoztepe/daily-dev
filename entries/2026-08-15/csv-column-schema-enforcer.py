import csv

def validate_csv(file_path, schema):
    """
    schema format: {'col_name': type_func}
    e.g., {'age': int, 'price': float}
    """
    errors = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            
            # Validate headers
            for field in schema:
                if field not in headers:
                    return [f"Missing required column: {field}"]

            # Validate rows
            for i, row in enumerate(reader, start=2):
                for col, cast_func in schema.items():
                    try:
                        cast_func(row[col])
                    except (ValueError, TypeError):
                        errors.append(f"Row {i}: Invalid data type in '{col}' (expected {cast_func.__name__})")
                    except KeyError:
                        errors.append(f"Row {i}: Missing value for '{col}'")
    except FileNotFoundError:
        return ["File not found"]
    return errors

def main():
    # Define expected columns and their target types
    csv_schema = {
        'id': int,
        'product': str,
        'price': float
    }
    
    # Simulate usage
    results = validate_csv('data.csv', csv_schema)
    if not results:
        print("CSV validation passed successfully.")
    else:
        print("Validation errors found:")
        for err in results:
            print(f"- {err}")

if __name__ == '__main__':
    main()
