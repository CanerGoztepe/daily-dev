def flatten_json(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '.')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '.')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out

def main():
    import json
    sample_data = {
        "user": {
            "id": 101,
            "profile": {
                "name": "Alice",
                "tags": ["admin", "editor"]
            }
        },
        "active": True
    }
    
    try:
        flattened = flatten_json(sample_data)
        print(json.dumps(flattened, indent=4))
    except Exception as e:
        print(f"Error processing JSON: {e}")

if __name__ == "__main__":
    main()
