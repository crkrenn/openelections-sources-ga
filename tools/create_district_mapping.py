import json
import re
import sys
import diskcache
from pathlib import Path
import argparse

def create_district_mapping(json_file_path, cache_dir=".district_cache"):
    """
    Creates a mapping of IDs to district strings from a JSON file, using diskcache for persistence.

    Args:
        json_file_path (str): Path to the JSON file
        cache_dir (str): Directory to store the diskcache

    Returns:
        dict: Mapping of IDs to district strings
    """
    # Create cache instance
    cache = diskcache.Cache(cache_dir)

    # Create cache key based on file path and modification time
    file_path = Path(json_file_path)
    if not file_path.exists():
        print(f"Error: File {json_file_path} not found")
        return {}

    cache_key = f"{file_path.absolute()}_{file_path.stat().st_mtime}"

    # Check if we have cached results
    cached_mapping = cache.get(cache_key)
    if cached_mapping is not None:
        print("Using cached district mapping")
        return cached_mapping

    print("Processing JSON file and creating new mapping")

    # Dictionary to store id -> district mapping
    district_map = {}

    try:
        # Read and parse JSON file
        with open(json_file_path, 'r') as file:
            data = json.load(file)

        # Function to extract district number from name
        def extract_district_number(name):
            if "State House of Representatives - District" not in name:
                return None
            match = re.search(r'District (\d+)', name)
            return match.group(1) if match else None

        # Process items recursively
        def process_items(items):
            if isinstance(items, dict):
                if 'id' in items and 'name' in items:
                    district_num = extract_district_number(items['name'])
                    if district_num:
                        district_map[items['id']] = f"District {district_num}"
                for value in items.values():
                    process_items(value)
            elif isinstance(items, list):
                for item in items:
                    process_items(item)

        # Process the JSON data
        process_items(data)

        # Store in cache
        cache.set(cache_key, district_map)

        return district_map

    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {json_file_path}")
        return {}
    except Exception as e:
        print(f"Error: {str(e)}")
        return {}
    finally:
        cache.close()


def create_precinct_mapping(json_file_path, cache_dir=".precinct_cache"):
    """
    Creates a mapping of precinct names to their associated districts from a JSON file.

    Args:
        json_file_path (str): Path to the JSON file
        cache_dir (str): Directory to store the diskcache

    Returns:
        dict: Mapping of precinct names to list of district numbers
    """
    # Create cache instance
    cache = diskcache.Cache(cache_dir)

    # Create cache key based on file path and modification time
    file_path = Path(json_file_path)
    if not file_path.exists():
        print(f"Error: File {json_file_path} not found")
        return {}

    cache_key = f"precinct_map_{file_path.absolute()}_{file_path.stat().st_mtime}"

    # Check if we have cached results
    cached_mapping = cache.get(cache_key)
    if cached_mapping is not None:
        print("Using cached precinct mapping")
        return cached_mapping

    print("Processing JSON file and creating new precinct mapping")

    # Dictionary to store precinct -> districts mapping
    precinct_map = defaultdict(set)

    try:
        # Read and parse JSON file
        with open(json_file_path, 'r') as file:
            data = json.load(file)

        def extract_district_number(name):
            if "State House of Representatives - District" not in name:
                return None
            match = re.search(r'District (\d+)', name)
            return match.group(1) if match else None

        def process_ballot_options(ballot_options, district_num):
            for option in ballot_options:
                if 'precinctResults' in option:
                    for precinct in option['precinctResults']:
                        if 'name' in precinct and not precinct.get('isVirtual', False):
                            precinct_map[precinct['name']].add(district_num)

        def process_items(items):
            if isinstance(items, dict):
                if 'name' in items and 'ballotOptions' in items:
                    district_num = extract_district_number(items['name'])
                    if district_num:
                        process_ballot_options(items['ballotOptions'], district_num)
                for value in items.values():
                    process_items(value)
            elif isinstance(items, list):
                for item in items:
                    process_items(item)

        # Process the JSON data
        process_items(data)

        # Convert sets to sorted lists for JSON serialization
        final_map = {precinct: sorted(list(districts))
                    for precinct, districts in precinct_map.items()}

        # Store in cache
        cache.set(cache_key, final_map)

        return final_map

    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {json_file_path}")
        return {}
    except Exception as e:
        print(f"Error: {str(e)}")
        return {}
    finally:
        cache.close()



def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Create district ID mapping from JSON file')
    parser.add_argument('json_file', help='Path to the JSON file to process')
    parser.add_argument('--cache-dir', default='district_cache',
                       help='Directory to store the cache (default: .district_cache)')
    parser.add_argument('--lookup', help='Look up specific district ID')

    args = parser.parse_args()



    # Create the mapping
    mapping = create_district_mapping(args.json_file, args.cache_dir)

    if args.lookup:
        # Look up specific district
        district = mapping.get(args.lookup)
        if district:
            print(f"ID {args.lookup}: {district}")
        else:
            print(f"No district found for ID {args.lookup}")
    else:
        # Print all mappings
        if mapping:
            print("\nDistrict Mappings:")
            for id_num, district in sorted(mapping.items()):
                print(f"ID: {id_num} -> {district}")
        else:
            print("No mappings found")

if __name__ == "__main__":
    main()