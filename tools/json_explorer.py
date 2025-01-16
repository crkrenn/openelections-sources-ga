import json
from collections import Counter
from pprint import pprint
import sys
import argparse

def analyze_json_structure(json_data, max_items=3):
    """Analyze and print insights about a JSON structure"""
    
    def get_type_info(obj, path="root"):
        """Recursively get information about types and structures"""
        if isinstance(obj, dict):
            print(f"\nKeys at {path}:")
            pprint(list(obj.keys())[:max_items])
            print(f"Total keys: {len(obj)}")
            
            # Sample a few values
            print(f"\nSample values from {path}:")
            for k, v in list(obj.items())[:max_items]:
                print(f"{k}: {type(v).__name__}")
                
            # Recurse into nested structures
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    get_type_info(v, f"{path}.{k}")
                    
        elif isinstance(obj, list):
            print(f"\nArray at {path}:")
            print(f"Length: {len(obj)}")
            
            # Analyze types in the array
            types = Counter(type(x).__name__ for x in obj)
            print("Value types in array:", dict(types))
            
            # Sample a few items
            if obj:
                print("\nSample items:")
                pprint(obj[:max_items])
                
                # If items are dictionaries, analyze their keys
                if isinstance(obj[0], dict):
                    key_freq = Counter(k for d in obj for k in d.keys())
                    print("\nCommon keys across objects:")
                    pprint(dict(key_freq.most_common(5)))

def analyze_streaming(filename):
    """Analyze a large JSON file using streaming"""
    import ijson  # pip install ijson
    
    with open(filename, 'rb') as f:
        parser = ijson.parse(f)
        
        current_path = []
        structure = {}
        
        for prefix, event, value in parser:
            if event == 'start_map':
                current_path.append(prefix)
            elif event == 'end_map':
                current_path.pop()
            elif event == 'map_key':
                full_path = '.'.join(filter(None, current_path + [value]))
                structure[full_path] = None
                
        print("JSON paths found:")
        pprint(list(structure.keys()))

def main():
    parser = argparse.ArgumentParser(description='Analyze JSON file structure')
    parser.add_argument('filename', help='Path to the JSON file to analyze')
    parser.add_argument('--stream', action='store_true', 
                      help='Use streaming parser for very large files')
    parser.add_argument('--max-items', type=int, default=3,
                      help='Maximum number of items to show in samples (default: 3)')
    
    args = parser.parse_args()
    
    try:
        if args.stream:
            analyze_streaming(args.filename)
        else:
            with open(args.filename) as f:
                data = json.load(f)
                analyze_json_structure(data, args.max_items)
    except FileNotFoundError:
        print(f"Error: File '{args.filename}' not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON file - {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
