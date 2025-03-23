#!/usr/bin/env python3
"""
Utility script to check CricAPI availability and validate the API key.
This can be run before using the main application to ensure the API is working.
"""

import requests
import json
import os
import sys

# Default API key from the example
DEFAULT_API_KEY = "9de714ba-d89b-40de-adae-2c3f544c477a"

def check_api_status(api_key):
    """Check if the CricAPI is available and the API key is valid"""
    base_url = "https://api.cricapi.com/v1"
    
    # Test with the currentMatches endpoint as it's simpler
    endpoint = f"{base_url}/currentMatches"
    params = {
        "apikey": api_key,
        "offset": 0
    }
    
    print(f"Checking CricAPI status with key: {api_key}")
    
    try:
        response = requests.get(endpoint, params=params)
        
        # Pretty print the response for debugging
        data = response.json()
        
        if response.status_code == 200:
            if data.get("status") == "success":
                print("✅ API is available and key is valid!")
                print(f"Credit information:")
                print(f"  - Status: {data.get('status')}")
                print(f"  - Info: {data.get('info', {})}")
                return True
            else:
                print("❌ API key may be invalid or rate limited.")
                print(f"Error: {data.get('status')} - {data.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ API returned status code {response.status_code}")
            print(f"Error: {data.get('message', 'Unknown error')}")
            return False
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to API: {e}")
        return False
    except json.JSONDecodeError:
        print("❌ Error decoding API response. Response is not valid JSON.")
        return False

def main():
    # Get API key from environment variable or use default
    api_key = os.environ.get("CRICAPI_KEY", DEFAULT_API_KEY)
    
    print("CricAPI Status Checker")
    print("=====================")
    
    # Check if the API key is provided as a command-line argument
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
        print(f"Using API key from command line: {api_key}")
    
    # Check API status
    status = check_api_status(api_key)
    
    # Exit with appropriate status code
    sys.exit(0 if status else 1)

if __name__ == "__main__":
    main() 