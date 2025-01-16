import json
import re
import sys
import diskcache
from pathlib import Path
import argparse
from collections import defaultdict

def create_precinct_mapping(json_file_path, cache_dir="precinct_cache"):
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
            print(f"Successfully loaded JSON file: {json_file_path}")

        def extract_district_number(name):
            if not name or "State House of Representatives - District" not in name:
                return None
            match = re.search(r'District (\d+)', name)
            return match.group(1) if match else None

        def process_ballot_options(ballot_options, district_num):
            if not ballot_options or not isinstance(ballot_options, list):
                print(f"Warning: Invalid ballot_options: {ballot_options}")
                return

            for option in ballot_options:
                if not isinstance(option, dict):
                    continue

                precinct_results = option.get('precinctResults', [])
                if not precinct_results:
                    continue

                for precinct in precinct_results:
                    if not isinstance(precinct, dict):
                        continue

                    precinct_name = precinct.get('name')
                    is_virtual = precinct.get('isVirtual', False)

                    if precinct_name and not is_virtual:
                        precinct_map[precinct_name].add(district_num)

        def process_items(items):
            if not items:
                return

            if isinstance(items, dict):
                name = items.get('name', '')
                ballot_options = items.get('ballotOptions')

                if name and ballot_options:
                    district_num = extract_district_number(name)
                    if district_num:
                        process_ballot_options(ballot_options, district_num)

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

        print(f"Found {len(final_map)} precincts")

        # Store in cache
        cache.set(cache_key, final_map)

        return final_map

    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {json_file_path}")
        return {}
    except Exception as e:
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return {}
    finally:
        cache.close()

# def main():
#     parser = argparse.ArgumentParser(description='Create precinct to district mapping from JSON file')
#     parser.add_argument('json_file', help='Path to the JSON file to process')
#     parser.add_argument('--cache-dir', default='precinct_cache',
#                        help='Directory to store the cache (default: precinct_cache)')
#     parser.add_argument('--lookup', help='Look up specific precinct')
#     parser.add_argument('--districts', nargs='+', type=str,
#                        help='List of districts to filter by (e.g., --districts 2 3 4)')

#     args = parser.parse_args()

#     # Create the mapping
#     mapping = create_precinct_mapping(args.json_file, args.cache_dir)

#     if args.lookup:
#         # Look up specific precinct
#         districts = mapping.get(args.lookup)
#         if districts:
#             if args.districts:
#                 filtered_districts = [d for d in districts if d in args.districts]
#                 if filtered_districts:
#                     print(f"\nPrecinct '{args.lookup}' is in districts: {', '.join(filtered_districts)}")
#                 else:
#                     print(f"\nPrecinct '{args.lookup}' is not in any of the specified districts")
#             else:
#                 print(f"\nPrecinct '{args.lookup}' is in districts: {', '.join(districts)}")
#         else:
#             print(f"\nNo districts found for precinct '{args.lookup}'")
#     else:
#         # Print all mappings
#         if mapping:
#             print("\nPrecinct to District Mappings:")
#             for precinct, districts in sorted(mapping.items()):
#                 if args.districts:
#                     filtered_districts = [d for d in districts if d in args.districts]
#                     if filtered_districts:
#                         print(f"Precinct: {precinct} -> Districts: {', '.join(filtered_districts)}")
#                 else:
#                     print(f"Precinct: {precinct} -> Districts: {', '.join(districts)}")

#             # Create inverse mapping (district to precincts)
#             inverse_mapping = defaultdict(set)
#             for precinct, districts in mapping.items():
#                 for district in districts:
#                     if not args.districts or district in args.districts:
#                         inverse_mapping[district].add(precinct)

#             print("\nDistrict to Precinct Mappings:")
#             for district, precincts in sorted(inverse_mapping.items()):
#                 print(f"District: {district} -> Precincts: {', '.join(sorted(precincts))}")
#         else:
#             print("No mappings found")

def main():
    parser = argparse.ArgumentParser(description='Create precinct to district mapping from JSON file')
    parser.add_argument('json_file', help='Path to the JSON file to process')
    parser.add_argument('--cache-dir', default='precinct_cache',
                       help='Directory to store the cache (default: precinct_cache)')
    parser.add_argument('--lookup', help='Look up specific precinct')
    parser.add_argument('--districts', nargs='+', type=str,
                       help='List of districts to filter by (e.g., --districts 2 3 4)')

    args = parser.parse_args()

    # Create the mapping
    mapping = create_precinct_mapping(args.json_file, args.cache_dir)

    if args.lookup:
        # Look up specific precinct
        districts = mapping.get(args.lookup)
        if districts:
            if args.districts:
                filtered_districts = [d for d in districts if d in args.districts]
                if filtered_districts:
                    print(f"\nPrecinct '{args.lookup}' is in districts: {', '.join(filtered_districts)}")
                else:
                    print(f"\nPrecinct '{args.lookup}' is not in any of the specified districts")
            else:
                print(f"\nPrecinct '{args.lookup}' is in districts: {', '.join(districts)}")
        else:
            print(f"\nNo districts found for precinct '{args.lookup}'")
    else:
        # Print all mappings
        if mapping:
            print("\nPrecinct to District Mappings:")
            for precinct, districts in sorted(mapping.items()):
                if args.districts:
                    filtered_districts = [d for d in districts if d in args.districts]
                    if filtered_districts:
                        print(f"Precinct: {precinct} -> Districts: {', '.join(filtered_districts)}")
                else:
                    print(f"Precinct: {precinct} -> Districts: {', '.join(districts)}")

            # Create inverse mapping (district to precincts)
            inverse_mapping = defaultdict(set)
            for precinct, districts in mapping.items():
                for district in districts:
                    if not args.districts or district in args.districts:
                        inverse_mapping[district].add(precinct)

            print("\nDistrict to Precinct Mappings:")
            for district, precincts in sorted(inverse_mapping.items()):
                print(f"District: {district} -> Precincts: {', '.join(sorted(precincts))}")

            # Create mapping of districts to unique precincts
            unique_precinct_mapping = defaultdict(set)
            for precinct, districts in mapping.items():
                if len(districts) == 1 and (not args.districts or districts[0] in args.districts):
                    unique_precinct_mapping[districts[0]].add(precinct)

            print("\nDistrict to Unique Precinct Mappings (precincts only in this district):")
            for district, precincts in sorted(unique_precinct_mapping.items()):
                print(f"District: {district} -> Unique Precincts: {', '.join(sorted(precincts))}")
                print(f"Total unique precincts: {len(precincts)}")
        else:
            print("No mappings found")

if __name__ == "__main__":
    main()
