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
from datetime import timedelta

# Constants
API_KEY = os.environ.get("CRICAPI_KEY", "")
DEBUG_SERIES_FILE = "debug_series_data.json"
DEBUG_MATCH_FILE = "debug_match_details.json"
PROCESSED_MATCHES_FILE = "processed_matches.json"
RUN_INTERVAL_HOURS = 6  # Run every 6 hours
MATCH_DATA_DIR = "match_data"

def save_debug_json(filename, data):
    """Save API response data to a debug file"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Debug data saved to {filename}")

def get_processed_matches():
    """Load the list of processed match IDs"""
    if os.path.exists(PROCESSED_MATCHES_FILE):
        with open(PROCESSED_MATCHES_FILE, 'r') as f:
            return json.load(f)
    return []

def save_processed_match(match_id):
    """Add a match ID to the processed matches list"""
    processed = get_processed_matches()
    if match_id not in processed:
        processed.append(match_id)
        with open(PROCESSED_MATCHES_FILE, 'w') as f:
            json.dump(processed, f)

def check_last_run():
    """Check if we should run based on the last execution time"""
    last_run_file = Path(".last_run")
    now = datetime.datetime.now()
    
    if last_run_file.exists():
        try:
            with open(last_run_file, 'r') as f:
                last_run_str = f.read().strip()
                last_run = datetime.datetime.fromisoformat(last_run_str)
                
                # If it's been less than RUN_INTERVAL_HOURS since the last run, skip
                if now - last_run < timedelta(hours=RUN_INTERVAL_HOURS):
                    hours_ago = (now - last_run).total_seconds() / 3600
                    print(f"Last run was {hours_ago:.1f} hours ago. Skipping.")
                    return False
        except Exception as e:
            print(f"Error reading last run time: {e}")
    
    # Update the last run time
    with open(last_run_file, 'w') as f:
        f.write(now.isoformat())
    
    return True

def main():
    """Main function to fetch and process cricket matches"""
    
    # Skip if we've run recently, unless force=True is specified
    if not check_last_run():
        return
    
    print(f"Starting cricket stats processing at {datetime.datetime.now().isoformat()}")
    
    # Initialize API client
    client = CricAPIClient(API_KEY)
    
    # Get processed match IDs
    processed_matches = get_processed_matches()
    print(f"Found {len(processed_matches)} previously processed matches")
    
    # Initialize stats processor
    stats_processor = StatsProcessor(client)
    
    # Get IPL series info
    series_info = client.get_series()
    if not series_info:
        print("Failed to fetch series information")
        return
    
    # Save series data for debugging
    save_debug_json(DEBUG_SERIES_FILE, series_info)
    
    # Get all matches for the series
    series_id = os.environ.get("SERIES_ID", "c75f8952-74d4-416f-b7b4-7da4b4e3ae6e")  # IPL 2023
    matches = client.get_all_matches(series_id)
    
    # Find all completed matches
    completed_matches = [m for m in matches if m.get("status") == "COMPLETED"]
    print(f"Found {len(completed_matches)} completed matches")
    
    # Only process matches that haven't been processed yet
    new_matches = [m for m in completed_matches if m.get("id") not in processed_matches]
    print(f"Found {len(new_matches)} new matches to process")
    
    if not new_matches:
        print("No new matches to process")
        return
    
    # Process match data
    for match in new_matches:
        match_id = match.get("id")
        match_name = match.get("name", "Unknown Match")
        
        print(f"Processing match: {match_name}")
        
        # Get match details
        match_details = client.get_match_details(match_id)
        if match_details:
            # Save match details for debugging
            if match_id and not os.path.exists(DEBUG_MATCH_FILE):
                save_debug_json(DEBUG_MATCH_FILE, match_details)
            
            # Process match data
            if stats_processor._process_match_data(match_id, match_details):
                # Calculate player scores for this match
                stats_processor.calculate_player_scores(match_id)
                # Mark as processed
                save_processed_match(match_id)
                print(f"Successfully processed match: {match_name}")
            else:
                print(f"No ball-by-ball data available for match: {match_name}")
        else:
            print(f"Failed to fetch match details for: {match_name}")
        
        # Add a short delay to avoid hitting rate limits
        time.sleep(1)
    
    # Save player statistics
    if stats_processor.player_stats:
        stats_processor.save_to_csv()
        stats_processor.save_to_json()
        print("Player statistics saved")
    else:
        print("No player statistics to save")

if __name__ == "__main__":
    main() 