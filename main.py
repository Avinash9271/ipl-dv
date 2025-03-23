#!/usr/bin/env python3
"""
Cricket Player Statistics Analyzer
This script fetches cricket match data from CricAPI, processes ball-by-ball information,
and generates player statistics in JSON format.
"""

import os
import sys
import json
import time
import datetime
import pathlib
from api_client import CricAPIClient
from stats_processor import StatsProcessor
from pathlib import Path

# Default API key and Series ID from the example
DEFAULT_API_KEY = "9de714ba-d89b-40de-adae-2c3f544c477a"
DEFAULT_SERIES_ID = "d5a498c8-7596-4b93-8ab0-e0efc3345312"
PROCESSED_MATCHES_FILE = "processed_matches.json"
LAST_RUN_FILE = "last_run_timestamp.txt"
RUN_INTERVAL_SECONDS = 600  # 10 minutes
MATCH_DATA_DIR = "match_data"

def save_debug_json(data, filename):
    """Save data to JSON file for debugging"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Debug data saved to {filename}")

def get_processed_matches():
    """Load already processed matches from file"""
    if not os.path.exists(PROCESSED_MATCHES_FILE):
        return {}
    
    try:
        with open(PROCESSED_MATCHES_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading processed matches: {e}")
        return {}

def save_processed_match(match_id, match_info):
    """Save a match as processed"""
    processed = get_processed_matches()
    processed[match_id] = {
        "id": match_id,
        "name": match_info.get("name", "Unknown"),
        "status": match_info.get("status", "Unknown"),
        "processed_at": datetime.datetime.now().isoformat()
    }
    
    with open(PROCESSED_MATCHES_FILE, 'w') as f:
        json.dump(processed, f, indent=2)

def check_last_run():
    """Check if enough time has passed since the last run"""
    if not os.path.exists(LAST_RUN_FILE):
        return True
    
    try:
        with open(LAST_RUN_FILE, 'r') as f:
            last_run_str = f.read().strip()
            if not last_run_str:
                return True
            
            last_run = datetime.datetime.fromisoformat(last_run_str)
            elapsed = (datetime.datetime.now() - last_run).total_seconds()
            
            if elapsed < RUN_INTERVAL_SECONDS:
                print(f"Last run was too recent ({elapsed:.1f} seconds ago). "
                      f"Please wait {RUN_INTERVAL_SECONDS - elapsed:.1f} more seconds.")
                return False
            return True
    except Exception as e:
        print(f"Error checking last run: {e}")
        return True

def update_last_run():
    """Update the last run timestamp"""
    with open(LAST_RUN_FILE, 'w') as f:
        f.write(datetime.datetime.now().isoformat())

def main():
    # Create match_data directory if it doesn't exist
    Path(MATCH_DATA_DIR).mkdir(exist_ok=True)
    
    # Check if enough time has passed since the last run
    if not check_last_run():
        return
    
    # Get processed matches
    processed_matches = get_processed_matches()
    
    # Initialize the API client
    client = CricAPIClient()
    
    # Fetch series information
    series = client.get_series()
    if not series:
        print("Failed to fetch series information.")
        return
    
    print(f"Fetched series: {series['info']['name']}")
    
    # Get match IDs for completed matches
    matches = client.get_all_matches(series.get('id'))
    if not matches:
        print("No matches found.")
        return
    
    completed_matches = [match for match in matches if match.get('status') == 'completed']
    print(f"Found {len(completed_matches)} completed matches.")
    
    # Filter out already processed matches
    new_matches = [match for match in completed_matches 
                   if match.get('id') not in processed_matches]
    
    if not new_matches:
        print("No new matches to process.")
        return
    
    print(f"Processing {len(new_matches)} new matches.")
    
    # Initialize the stats processor
    processor = StatsProcessor(client)
    
    # Process all match details and calculate player statistics
    successful_count = processor.process_all_matches(new_matches)
    
    # Save the processed matches
    for match in new_matches:
        save_processed_match(match.get('id'), match)
    
    # Update the last run timestamp
    update_last_run()
    
    if successful_count > 0:
        print(f"Processing complete. Player statistics saved.")
    else:
        print("No matches were successfully processed.")

if __name__ == "__main__":
    main() 