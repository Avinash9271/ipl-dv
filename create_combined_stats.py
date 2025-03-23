#!/usr/bin/env python3
"""
Create combined player and owner statistics for the simplified website.
"""

import json
import os

def main():
    # Load player stats
    try:
        with open("player_stats.json", "r") as f:
            player_stats = json.load(f)
    except FileNotFoundError:
        print("Error: player_stats.json not found.")
        return
    
    # Load owner_stats
    try:
        with open("owner_stats.json", "r") as f:
            owner_stats = json.load(f)
    except FileNotFoundError:
        print("Error: owner_stats.json not found.")
        return
    
    # Create a mapping of player_id to owner
    player_to_owner = {}
    for owner_name, owner_data in owner_stats.items():
        for player in owner_data.get("players", []):
            player_id = str(player.get("player_id"))
            player_to_owner[player_id] = owner_name
    
    # Create combined stats structure
    combined_stats = {}
    
    # Process player data
    for player_id, player_data in player_stats.get("players", {}).items():
        # Only include players with stats
        if player_data.get("batting", {}).get("runs", 0) > 0 or \
           player_data.get("bowling", {}).get("wickets", 0) > 0 or \
           player_data.get("fielding", {}).get("catches", 0) > 0 or \
           player_data.get("fielding", {}).get("run_outs", 0) > 0:
            
            # Add owner information
            owner = player_to_owner.get(player_id, "Unknown")
            
            # Create entry in combined stats
            combined_stats[player_id] = {
                "name": player_data.get("player_name", "Unknown Player"),
                "team": player_data.get("team", "Unknown Team"),
                "owner": owner,
                "total_score": player_data.get("total_score", 0),
                "batting": player_data.get("batting", {}),
                "bowling": player_data.get("bowling", {}),
                "fielding": player_data.get("fielding", {})
            }
    
    # Save the combined stats
    with open("combined_stats.json", "w") as f:
        json.dump(combined_stats, f, indent=2)
    
    print(f"Combined stats saved to combined_stats.json with {len(combined_stats)} player entries")

if __name__ == "__main__":
    main() 