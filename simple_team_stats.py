#!/usr/bin/env python3
"""
Simple Team Owner Statistics Analyzer
This script processes player statistics and attributes them to team owners,
outputting results to a JSON file and console.
GitHub Pages compatible version - removes investment statistics.
"""

import json
import csv
import pandas as pd
import os
import sys
from collections import defaultdict

def load_player_team_data(csv_file='teams.csv'):
    """Load the player to team and owner mapping"""
    player_teams = {}
    team_owners = defaultdict(list)
    owner_teams = defaultdict(set)
    
    try:
        df = pd.read_csv(csv_file)
        
        # Create mapping of player_id to team_id and owner
        for _, row in df.iterrows():
            player_id = row['player_id']
            team_id = row['team_id']
            player_name = row['player']
            owner_name = row['owner']
            
            player_teams[player_id] = {
                'team_id': team_id,
                'player_name': player_name,
                'owner': owner_name
            }
            
            team_owners[team_id].append({
                'player_id': player_id,
                'player_name': player_name,
                'owner': owner_name
            })
            
            owner_teams[owner_name].add(team_id)
        
        print(f"Loaded data for {len(player_teams)} players")
        print(f"Found {len(team_owners)} teams and {len(owner_teams)} owners")
        return player_teams, team_owners, owner_teams
    
    except Exception as e:
        print(f"Error loading team data: {e}")
        return {}, defaultdict(list), defaultdict(set)

def load_player_stats(json_file='player_stats.json'):
    """Load player statistics from JSON file"""
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Check if the structure is nested under 'players'
        if 'players' in data:
            player_stats = data['players']
        else:
            player_stats = data
            
        print(f"Loaded statistics for {len(player_stats)} players")
        return player_stats
    
    except Exception as e:
        print(f"Error loading player statistics: {e}")
        return {}

def map_player_ids(player_teams, player_stats):
    """Map player IDs from teams.csv to player_stats.json"""
    # Create a name-to-id mapping to handle ID mismatches
    name_to_team = {}
    for player_id, player_data in player_teams.items():
        player_name = player_data['player_name']
        name_to_team[player_name.lower()] = {
            'player_id': player_id,
            'team_id': player_data['team_id'],
            'owner': player_data['owner']
        }
    
    # Create a mapping from stats player_id to team player_id
    id_mapping = {}
    name_mapping = {}
    
    for stats_id, stats_data in player_stats.items():
        player_name = stats_data.get('player_name', '') or stats_data.get('name', '')
        player_name_lower = player_name.lower()
        
        if player_name_lower in name_to_team:
            id_mapping[stats_id] = name_to_team[player_name_lower]['player_id']
            name_mapping[player_name] = name_to_team[player_name_lower]
    
    print(f"Mapped {len(id_mapping)} player IDs between datasets")
    return id_mapping, name_mapping

def calculate_owner_stats(player_teams, player_stats, id_mapping):
    """Calculate aggregated statistics for each team owner"""
    owner_stats = defaultdict(lambda: {
        'total_runs': 0,
        'total_wickets': 0,
        'total_players': 0,
        'players': []
    })
    
    # Calculate stats for each player and aggregate by owner
    for stats_id, stats_data in player_stats.items():
        if stats_id in id_mapping:
            team_player_id = id_mapping[stats_id]
            if team_player_id in player_teams:
                owner = player_teams[team_player_id]['owner']
                team_id = player_teams[team_player_id]['team_id']
                player_name = player_teams[team_player_id]['player_name']
                
                # Get runs and wickets from stats
                if 'batting' in stats_data and 'runs' in stats_data['batting']:
                    # New structure
                    runs = stats_data['batting']['runs']
                    wickets = stats_data['bowling']['wickets'] if 'bowling' in stats_data else 0
                else:
                    # Old structure
                    runs = stats_data.get('runs', 0)
                    wickets = stats_data.get('wickets', 0)
                
                # Add to owner's aggregate stats
                owner_stats[owner]['total_runs'] += runs
                owner_stats[owner]['total_wickets'] += wickets
                owner_stats[owner]['total_players'] += 1
                
                # Add individual player stats
                owner_stats[owner]['players'].append({
                    'player_id': team_player_id,
                    'player_name': player_name,
                    'team_id': team_id,
                    'runs': runs,
                    'wickets': wickets
                })
    
    # Convert to standard dict
    return dict(owner_stats)

def print_owner_summary(owner_stats):
    """Print a summary of team owner statistics"""
    print("\n" + "="*80)
    print("TEAM OWNER PERFORMANCE SUMMARY".center(80))
    print("="*80)
    
    # Create a DataFrame for better display
    summary_data = []
    for owner, stats in owner_stats.items():
        summary_data.append({
            'Owner': owner,
            'Total Runs': stats['total_runs'],
            'Total Wickets': stats['total_wickets'],
            'Player Count': stats['total_players']
        })
    
    summary_df = pd.DataFrame(summary_data)
    
    # Sort by total runs
    summary_df = summary_df.sort_values('Total Runs', ascending=False)
    
    # Print the summary
    print(summary_df.to_string(index=False))
    
    print("\n" + "="*80)
    print("TOP PERFORMING PLAYERS BY OWNER".center(80))
    print("="*80)
    
    # For each owner, print their top 3 players by runs scored
    for owner, stats in owner_stats.items():
        print(f"\n{owner}'s Top Players:")
        
        if not stats['players']:
            print("  No player data available")
            continue
            
        # Sort players by runs scored
        sorted_players = sorted(stats['players'], key=lambda x: x['runs'], reverse=True)
        
        # Print top 3 or all if less than 3
        for i, player in enumerate(sorted_players[:3], 1):
            print(f"  {i}. {player['player_name']}: {player['runs']} runs, {player['wickets']} wickets")

def main():
    """Main function to process data and output statistics"""
    # Load player-team-owner data
    player_teams, team_owners, owner_teams = load_player_team_data()
    
    # Load player statistics
    player_stats = load_player_stats()
    
    # Map player IDs between datasets
    id_mapping, name_mapping = map_player_ids(player_teams, player_stats)
    
    # Calculate owner statistics
    owner_stats = calculate_owner_stats(player_teams, player_stats, id_mapping)
    
    # Print summary
    print_owner_summary(owner_stats)
    
    # Save the processed data
    with open('owner_stats.json', 'w') as f:
        json.dump(owner_stats, f, indent=2)
    
    print("\nOwner statistics saved to owner_stats.json")

if __name__ == "__main__":
    main() 