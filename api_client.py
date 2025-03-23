import requests
import json
import time
import os
from pathlib import Path

class CricAPIClient:
    """Client for interacting with CricAPI"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("CRICAPI_KEY", "")
        self.base_url = "https://api.cricapi.com/v1"
        self.headers = {
            "Content-Type": "application/json"
        }
        # Create match_data directory if it doesn't exist
        Path("match_data").mkdir(exist_ok=True)
    
    def get_series(self):
        """Get information about the IPL series"""
        endpoint = f"{self.base_url}/series_info"
        params = {
            "apikey": self.api_key,
            "id": os.environ.get("SERIES_ID", "c75f8952-74d4-416f-b7b4-7da4b4e3ae6e")  # Default to IPL 2023
        }
        
        try:
            response = requests.get(endpoint, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'success':
                return data.get('data', {})
            else:
                print(f"API returned an error: {data.get('message', 'Unknown error')}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching series info: {e}")
            return None
    
    def get_all_matches(self, series_id):
        """Get all matches for a series"""
        endpoint = f"{self.base_url}/series_matches"
        params = {
            "apikey": self.api_key,
            "id": series_id
        }
        
        try:
            response = requests.get(endpoint, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'success':
                return data.get('data', {}).get('matches', [])
            else:
                print(f"API returned an error: {data.get('message', 'Unknown error')}")
                return []
        except requests.exceptions.RequestException as e:
            print(f"Error fetching series matches: {e}")
            return []
    
    def get_match_details(self, match_id):
        """Get ball-by-ball details of a match"""
        # Check if we already have the match data saved
        match_file = Path(f"match_data/{match_id}.json")
        if match_file.exists():
            print(f"  Loading match data from local file: {match_file}")
            try:
                with open(match_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"  Error loading local match data: {e}")
                # If there's an error, we'll fetch from API as a fallback
        
        # Fetch from API if not found locally
        endpoint = f"{self.base_url}/match_bbb"
        params = {
            "apikey": self.api_key,
            "id": match_id
        }
        
        try:
            print(f"  Fetching match data from API for match: {match_id}")
            response = requests.get(endpoint, params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            # Save the match data to a file if successful
            if data.get('status') == 'success':
                # Save match data to disk
                with open(match_file, 'w') as f:
                    json.dump(data, f, indent=2)
                print(f"  Saved match data to {match_file}")
            
            return data
        except requests.exceptions.RequestException as e:
            print(f"  Error fetching match details for match ID {match_id}: {e}")
            return None
    
    def get_completed_matches(self, series_data):
        """Extract completed matches from series data"""
        completed_matches = []
        
        try:
            match_list = series_data.get("data", {}).get("matchList", [])
            for match in match_list:
                if match.get("matchEnded", False) is True:
                    completed_matches.append(match)
            
            return completed_matches
        except (KeyError, AttributeError) as e:
            print(f"Error extracting completed matches: {e}")
            return []
    
    def get_all_match_details(self, completed_matches, delay=1):
        """Get details for all completed matches with rate limiting"""
        match_details = []
        
        for match in completed_matches:
            match_id = match.get("id")
            if match_id:
                print(f"Fetching details for match: {match.get('name', match_id)}")
                details = self.get_match_details(match_id)
                
                # Save match details to a file for future reference
                if details and details.get('status') == 'success':
                    # Save match data to disk
                    match_file = Path(f"match_data/{match_id}.json")
                    with open(match_file, 'w') as f:
                        json.dump(details, f, indent=2)
                    print(f"  Saved match data to {match_file}")
                    
                    match_details.append(details)
                
                # Add delay to avoid hitting rate limits
                time.sleep(delay)
            
        return match_details 