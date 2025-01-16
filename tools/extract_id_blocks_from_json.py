import argparse
import json
from typing import List, Tuple

def find_all_positions(content: str, target_id: str) -> List[int]:
    """Find all positions of the target ID in the content."""
    positions = []
    search_str = f'"id": "{target_id}"'
    pos = content.find(search_str)
    
    while pos != -1:
        positions.append(pos)
        pos = content.find(search_str, pos + 1)
    
    return positions

def extract_json_object(content: str, start_pos: int) -> Tuple[str, int, int]:
    """
    Extract a complete JSON object given a starting position within it.
    Returns the object and its start/end positions.
    """
    # Search backwards for the opening bracket
    object_start = start_pos
    while object_start >= 0:
        if content[object_start] == '{':
            break
        object_start -= 1
    
    # Search forwards for the matching closing bracket
    object_end = start_pos
    bracket_count = 1  # We start with 1 since we found an opening bracket
    
    while object_end < len(content) and bracket_count > 0:
        object_end += 1
        if content[object_end] == '{':
            bracket_count += 1
        elif content[object_end] == '}':
            bracket_count -= 1
    
    if bracket_count == 0:
        return content[object_start:object_end + 1], object_start, object_end
    
    return None, -1, -1

def main():
    parser = argparse.ArgumentParser(description='Extract JSON objects with specific ID from file')
    parser.add_argument('filename', help='Path to the JSON file')
    parser.add_argument('id', help='ID to search for')
    
    args = parser.parse_args()
    
    try:
        with open(args.filename, 'r') as file:
            content = file.read()
        
        # Find all occurrences of the ID
        positions = find_all_positions(content, args.id)
        
        if not positions:
            # Output empty array if no matches
            print(json.dumps([]))
            return
        
        # Store results in a list
        results = []
        found_objects = set()  # Use set to avoid duplicates
        
        for pos in positions:
            obj, start, end = extract_json_object(content, pos)
            if obj:
                # Use tuple of start/end positions as key to identify unique objects
                obj_key = (start, end)
                if obj_key not in found_objects:
                    found_objects.add(obj_key)
                    try:
                        # Parse the extracted JSON object
                        parsed_obj = json.loads(obj)
                        result = {
                            "first_line": str(start),
                            "last_line": str(end),
                            "data": parsed_obj
                        }
                        results.append(result)
                    except json.JSONDecodeError:
                        # Skip invalid JSON objects
                        continue
        
        # Output the final JSON array
        print(json.dumps(results, indent=2))
            
    except FileNotFoundError:
        print(json.dumps({"error": f"File '{args.filename}' not found"}))
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()
