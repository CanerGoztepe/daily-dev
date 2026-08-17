import configparser
import os

def validate_config(file_path, schema):
    if not os.path.exists(file_path):
        return False, "File not found."
    
    config = configparser.ConfigParser()
    config.read(file_path)
    
    for (section, key), expected_type in schema.items():
        if not config.has_section(section):
            return False, f"Missing section: {section}"
        if not config.has_option(section, key):
            return False, f"Missing key: {key} in {section}"
        
        val = config.get(section, key)
        try:
            if expected_type == int:
                int(val)
            elif expected_type == bool:
                if val.lower() not in ['true', 'false', '1', '0', 'yes', 'no']:
                    raise ValueError
            elif expected_type == str:
                if not val.strip():
                    raise ValueError("Empty string")
        except ValueError:
            return False, f"Invalid type for {section}.{key}: expected {expected_type.__name__}"
    
    return True, "Validation successful."

if __name__ == '__main__':
    # Example schema: (section, key): type
    config_schema = {
        ('server', 'port'): int,
        ('server', 'enabled'): bool,
        ('database', 'host'): str
    }
    
    # Usage: python validator.py
    # config.ini content:
    # [server]
    # port = 8080
    # enabled = true
    # [database]
    # host = localhost
    
    success, message = validate_config('config.ini', config_schema)
    print(f"Status: {success}, Message: {message}")
