#!/usr/bin/env python3
"""
Team Owner Statistics Analyzer
This script processes player statistics and attributes them to team owners.
GitHub Pages compatible version - removes investment statistics.
"""

import json
import csv
import pandas as pd
import os
import sys
from collections import defaultdict
import dash
from dash import dcc, html, dash_table
import plotly.express as px
import plotly.graph_objects as go

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

def create_dashboard(owner_stats):
    """Create a Dash web application to visualize the statistics"""
    app = dash.Dash(__name__, 
                   suppress_callback_exceptions=True,
                   meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}])
    
    # Set page title for GitHub Pages
    app.title = "Cricket Team Owner Statistics"
    
    # Prepare data for visualizations
    owners = list(owner_stats.keys())
    total_runs = [stats['total_runs'] for stats in owner_stats.values()]
    total_wickets = [stats['total_wickets'] for stats in owner_stats.values()]
    
    # Create DataFrames for tables
    owner_df = pd.DataFrame({
        'Owner': owners,
        'Total Runs': total_runs,
        'Total Wickets': total_wickets,
        'Player Count': [stats['total_players'] for stats in owner_stats.values()]
    })
    
    # Create player-level DataFrame
    player_data = []
    for owner, stats in owner_stats.items():
        for player in stats['players']:
            player_data.append({
                'Owner': owner,
                'Player': player['player_name'],
                'Team ID': player['team_id'],
                'Runs': player['runs'],
                'Wickets': player['wickets']
            })
    
    player_df = pd.DataFrame(player_data)
    
    # Create dashboard layout
    app.layout = html.Div([
        html.H1("Cricket Team Owner Statistics", style={'textAlign': 'center'}),
        
        html.Div([
            html.H2("Owner Performance Summary"),
            dash_table.DataTable(
                id='owner-table',
                columns=[{"name": i, "id": i} for i in owner_df.columns],
                data=owner_df.to_dict('records'),
                style_cell={'textAlign': 'left'},
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                },
                sort_action='native',
                filter_action='native'
            )
        ]),
        
        html.Div([
            html.Div([
                html.H2("Total Runs by Owner"),
                dcc.Graph(
                    id='runs-graph',
                    figure=px.bar(
                        owner_df, 
                        x='Owner', 
                        y='Total Runs',
                        color='Owner',
                        title='Total Runs Scored by Each Owner\'s Players'
                    )
                )
            ], style={'width': '48%', 'display': 'inline-block'}),
            
            html.Div([
                html.H2("Total Wickets by Owner"),
                dcc.Graph(
                    id='wickets-graph',
                    figure=px.bar(
                        owner_df, 
                        x='Owner', 
                        y='Total Wickets',
                        color='Owner',
                        title='Total Wickets Taken by Each Owner\'s Players'
                    )
                )
            ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'})
        ]),
        
        html.Div([
            html.H2("All Players Data"),
            dash_table.DataTable(
                id='player-table',
                columns=[{"name": i, "id": i} for i in player_df.columns],
                data=player_df.to_dict('records'),
                style_cell={'textAlign': 'left'},
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold'
                },
                sort_action='native',
                filter_action='native',
                page_size=10
            )
        ]),
        
        html.Div([
            html.H2("Player Performance by Owner"),
            dcc.Dropdown(
                id='owner-dropdown',
                options=[{'label': owner, 'value': owner} for owner in owners],
                value=owners[0] if owners else None,
                style={'width': '50%'}
            ),
            dcc.Graph(id='owner-players-graph')
        ]),
        
        # Footer
        html.Div([
            html.Hr(),
            html.P("Cricket Team Owner Statistics Dashboard - Created with Dash",
                   style={'textAlign': 'center'})
        ])
    ])
    
    # Callback for the dropdown filter
    @app.callback(
        dash.dependencies.Output('owner-players-graph', 'figure'),
        [dash.dependencies.Input('owner-dropdown', 'value')]
    )
    def update_owner_graph(selected_owner):
        if not selected_owner:
            return go.Figure()
        
        filtered_df = player_df[player_df['Owner'] == selected_owner]
        return px.bar(
            filtered_df,
            x='Player',
            y='Runs',
            color='Player',
            title=f'Runs Scored by {selected_owner}\'s Players',
            hover_data=['Wickets']
        )
    
    return app

def main():
    """Main function to process data and launch dashboard"""
    # Load player-team-owner data
    player_teams, team_owners, owner_teams = load_player_team_data()
    
    # Load player statistics
    player_stats = load_player_stats()
    
    # Map player IDs between datasets
    id_mapping, name_mapping = map_player_ids(player_teams, player_stats)
    
    # Calculate owner statistics
    owner_stats = calculate_owner_stats(player_teams, player_stats, id_mapping)
    
    # Create and launch dashboard
    app = create_dashboard(owner_stats)
    
    # Save the processed data
    with open('owner_stats.json', 'w') as f:
        json.dump(owner_stats, f, indent=2)
    
    print("Owner statistics saved to owner_stats.json")
    print("Starting dashboard. Open your browser at http://127.0.0.1:8050/")
    
    # Run the dashboard
    app.run(debug=True)

if __name__ == "__main__":
    main() 