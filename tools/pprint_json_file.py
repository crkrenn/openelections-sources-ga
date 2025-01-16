"""
pprint_json_file.py
"""
import json
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] == "-h" or sys.argv[1] == "--help":
        print("Usage: python pprint_json_file.py <json_file>")
        sys.exit()

    for json_file in sys.argv[1:]:
        with open(json_file, "r") as f:
            json_data = json.load(f)
            formatted = (json.dumps(json_data, indent=2)
                       .replace(": {", ":\n{")
                       .replace(": [", ":\n["))
            print(formatted)