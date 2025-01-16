import json
import sys
from typing import List, Dict

def analyze_election_results(json_file: str, candidate_names: str, precinct_names: str) -> None:
    """
    Analyze election results from a JSON file for specified candidates and precincts.
    
    Args:
        json_file (str): Path to the JSON file containing election data
        candidate_names (str): Comma-separated list of candidate names
        precinct_names (str): Comma-separated list of precinct names
    """
    # Parse input parameters
    candidates = [name.strip() for name in candidate_names.split(',')]
    precincts = [name.strip() for name in precinct_names.split(',')]
    
    # Initialize results dictionary
    results: Dict[str, Dict[str, int]] = {
        candidate: {precinct: 0 for precinct in precincts}
        for candidate in candidates
    }
    
    # Initialize candidate totals
    candidate_totals = {candidate: 0 for candidate in candidates}
    
    try:
        # Read and parse JSON file
        with open(json_file, 'r') as f:
            data = json.load(f)
            
        # Process each candidate's data
        for candidate_data in data:
            candidate_name = candidate_data['name']
            if candidate_name in candidates:
                # Process precinct results
                for precinct_result in candidate_data['precinctResults']:
                    precinct_name = precinct_result['name']
                    if precinct_name in precincts:
                        vote_count = precinct_result['voteCount']
                        results[candidate_name][precinct_name] = vote_count
                        candidate_totals[candidate_name] += vote_count
        
        # Print results
        print("\nElection Results Analysis")
        print("=" * 50)
        
        # Print precinct-wise results
        print("\nPrecinct-wise Results:")
        print("-" * 30)
        for precinct in precincts:
            print(f"\nPrecinct: {precinct}")
            for candidate in candidates:
                votes = results[candidate][precinct]
                print(f"{candidate}: {votes:,} votes")
        
        # Print total results
        print("\nTotal Results:")
        print("-" * 30)
        for candidate in candidates:
            total = candidate_totals[candidate]
            print(f"{candidate}: {total:,} total votes")
            
    except FileNotFoundError:
        print(f"Error: Could not find file '{json_file}'")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in file '{json_file}'")
    except Exception as e:
        print(f"Error: An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <json_file> \"<candidate_names>\" \"<precinct_names>\"")
        sys.exit(1)
    
    json_file = sys.argv[1]
    candidate_names = sys.argv[2]
    precinct_names = sys.argv[3]
    
    analyze_election_results(json_file, candidate_names, precinct_names)
