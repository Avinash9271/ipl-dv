#!/usr/bin/env python3
"""
Test script to generate match data for scoring calculation testing.
"""

import json
import os
from collections import defaultdict

def generate_sample_data():
    """Generate sample player data for two matches with the same players."""
    # Match 1 data
    match1_data = {
        "p1_match1": {
            "player_id": "p1",
            "player_name": "Virat Kohli",
            "match_id": "match1",
            "team_id": "RCB",
            "runs": 75,
            "balls": 50,
            "wickets": 0,
            "catches": 1,
            "run_outs": 0,
            "wicket_bowled_or_lbw": 0,
            "owner": "Sai"
        },
        "p2_match1": {
            "player_id": "p2",
            "player_name": "Jasprit Bumrah",
            "match_id": "match1",
            "team_id": "MI",
            "runs": 5,
            "balls": 10,
            "wickets": 3,
            "catches": 0,
            "run_outs": 0,
            "wicket_bowled_or_lbw": 2,  # 2 of 3 wickets are bowled/lbw
            "owner": "Rohan"
        },
        "p3_match1": {
            "player_id": "p3",
            "player_name": "Suryakumar Yadav",
            "match_id": "match1",
            "team_id": "MI",
            "runs": 30,
            "balls": 20,
            "wickets": 0,
            "catches": 2,
            "run_outs": 1,
            "wicket_bowled_or_lbw": 0,
            "owner": "Dhruv"
        }
    }
    
    # Match 2 data - same players, different stats
    match2_data = {
        "p1_match2": {
            "player_id": "p1",
            "player_name": "Virat Kohli",
            "match_id": "match2",
            "team_id": "RCB",
            "runs": 25,
            "balls": 20,
            "wickets": 0,
            "catches": 0,
            "run_outs": 0,
            "wicket_bowled_or_lbw": 0,
            "owner": "Sai"
        },
        "p2_match2": {
            "player_id": "p2",
            "player_name": "Jasprit Bumrah",
            "match_id": "match2",
            "team_id": "MI",
            "runs": 0,
            "balls": 0,
            "wickets": 5,
            "catches": 1,
            "run_outs": 0,
            "wicket_bowled_or_lbw": 3,  # 3 of 5 wickets are bowled/lbw
            "owner": "Rohan"
        },
        "p3_match2": {
            "player_id": "p3",
            "player_name": "Suryakumar Yadav",
            "match_id": "match2",
            "team_id": "MI",
            "runs": 105,
            "balls": 60,
            "wickets": 0,
            "catches": 0,
            "run_outs": 0,
            "wicket_bowled_or_lbw": 0,
            "owner": "Dhruv"
        }
    }
    
    # Combine all data
    all_data = {**match1_data, **match2_data}
    
    return all_data

def calculate_score(player_data):
    """Calculate a player's score based on the provided formula."""
    runs = player_data.get('runs', 0)
    wickets = player_data.get('wickets', 0)
    catches = player_data.get('catches', 0)
    run_outs = player_data.get('run_outs', 0)
    wicket_bowled_or_lbw = player_data.get('wicket_bowled_or_lbw', 0)
    
    # Calculate batsman score component
    batsman_score = 0
    if runs > 0:
        batsman_score = runs + (8 if runs >= 50 else 0) + (8 if runs >= 100 else 0)
    
    # Calculate bowlers score component
    # Only count "good ones" (lbw, bowled, caught and bowled) for 20 points
    bowler_score = (wicket_bowled_or_lbw * 20) + ((wickets - wicket_bowled_or_lbw) * 16)
    bowler_score += (15 if wickets >= 3 else 0)
    
    # Calculate fielding score component
    fielding_score = (catches * 8) + (run_outs * 8)
    
    # Base score of 4 points for everyone
    base_score = 4
    
    total_score = batsman_score + bowler_score + fielding_score + base_score
    
    return {
        'batsman_score': batsman_score,
        'bowler_score': bowler_score,
        'fielding_score': fielding_score,
        'base_score': base_score,
        'total_score': total_score
    }

def find_highest_scorer_per_match(player_data):
    """Find the highest scorer in each match and apply the 1.3x multiplier."""
    matches = defaultdict(dict)
    
    # Group players by match
    for player_id, player in player_data.items():
        match_id = player.get('match_id', 'unknown')
        score_info = calculate_score(player)
        
        # Store player with their score info
        matches[match_id][player_id] = {
            'player_id': player_id,
            'player_name': player.get('player_name', 'Unknown'),
            'owner': player.get('owner', 'Unknown'),
            'score_info': score_info,
            'total_score': score_info['total_score']
        }
    
    # Find highest scorer in each match
    for match_id, match_players in matches.items():
        highest_score = 0
        highest_scorer = None
        
        for player_id, player_info in match_players.items():
            if player_info['total_score'] > highest_score:
                highest_score = player_info['total_score']
                highest_scorer = player_id
        
        if highest_scorer:
            # Apply 1.3x multiplier to the highest scorer
            match_players[highest_scorer]['is_highest_scorer'] = True
            match_players[highest_scorer]['original_score'] = match_players[highest_scorer]['total_score']
            match_players[highest_scorer]['total_score'] *= 1.3
    
    return matches

def organize_by_owner(matches_data, player_data):
    """Organize player data by owner for scoring."""
    owner_stats = defaultdict(lambda: {
        'total_score': 0,
        'total_players': 0,
        'players': []
    })
    
    # Group by owner for each match
    for player_id, player in player_data.items():
        owner = player.get('owner', 'Unknown')
        match_id = player.get('match_id', 'unknown')
        
        # Find the matches data for this player and match
        match_data = None
        if match_id in matches_data and player_id in matches_data[match_id]:
            match_data = matches_data[match_id][player_id]
        
        if not match_data:
            continue
        
        # Create player entry with complete data
        player_entry = {
            'player_id': player_id,
            'player_name': player.get('player_name', 'Unknown'),
            'team_id': player.get('team_id', 'Unknown'),
            'match_id': match_id,
            'runs': player.get('runs', 0),
            'wickets': player.get('wickets', 0),
            'catches': player.get('catches', 0),
            'run_outs': player.get('run_outs', 0),
            'wicket_bowled_or_lbw': player.get('wicket_bowled_or_lbw', 0),
            'score': match_data['total_score'],
            'is_highest_scorer': match_data.get('is_highest_scorer', False)
        }
        
        # Add to owner's stats
        owner_stats[owner]['players'].append(player_entry)
        owner_stats[owner]['total_score'] += match_data['total_score']
    
    # Count unique players per owner
    for owner, stats in owner_stats.items():
        unique_players = set()
        for player in stats['players']:
            # Use the actual player_id, not the entry ID which includes match info
            unique_players.add(player.get('player_id').split('_')[0])
        stats['total_players'] = len(unique_players)
    
    return dict(owner_stats)

def main():
    """Main test function."""
    # Generate sample data
    player_data = generate_sample_data()
    
    # Calculate scores and find highest scorer per match
    matches_data = find_highest_scorer_per_match(player_data)
    
    # Organize by owner
    owner_stats = organize_by_owner(matches_data, player_data)
    
    # Print results
    print("\n=== PLAYER SCORES BY MATCH ===")
    for match_id, match_players in matches_data.items():
        print(f"\nMatch: {match_id}")
        for player_id, player_info in match_players.items():
            highest_scorer = "⭐ (1.3x)" if player_info.get('is_highest_scorer') else ""
            print(f"  {player_info['player_name']} ({player_info['owner']}): {player_info['total_score']:.2f} {highest_scorer}")
            score_info = player_info['score_info']
            print(f"    Batting: {score_info['batsman_score']}, Bowling: {score_info['bowler_score']}, Fielding: {score_info['fielding_score']}")
    
    print("\n=== OWNER TOTALS ===")
    sorted_owners = sorted(owner_stats.items(), key=lambda x: x[1]['total_score'], reverse=True)
    for owner, stats in sorted_owners:
        print(f"{owner}: {stats['total_score']:.2f} points ({stats['total_players']} players)")
    
    # Save to owner_stats.json for testing
    with open('test_owner_stats.json', 'w') as f:
        json.dump(owner_stats, f, indent=2)
    
    print(f"\nData saved to test_owner_stats.json")

if __name__ == "__main__":
    main() 