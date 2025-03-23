#!/usr/bin/env python3
"""
Build Static Assets for GitHub Pages
This script creates static assets for deploying the Team Owner Statistics Dashboard
to GitHub Pages.
"""

import os
import json
import shutil
from pathlib import Path
import dash
from dash import dcc, html, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from collections import defaultdict

# Import functions from team_owner_stats.py
from team_owner_stats import (
    load_player_team_data,
    load_player_stats,
    map_player_ids,
    calculate_owner_stats,
    create_dashboard
)

def ensure_dir(directory):
    """Make sure directory exists"""
    Path(directory).mkdir(parents=True, exist_ok=True)

def create_style_css():
    """Create CSS file for the dashboard"""
    css_content = """
    body {
        font-family: Arial, sans-serif;
        margin: 0;
        padding: 20px;
        background-color: #f5f5f5;
    }
    
    .loading {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100vh;
    }
    
    .loading-spinner {
        border: 16px solid #f3f3f3;
        border-top: 16px solid #3498db;
        border-radius: 50%;
        width: 80px;
        height: 80px;
        animation: spin 2s linear infinite;
        margin-bottom: 20px;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    h1, h2 {
        color: #2c3e50;
    }
    
    h1 {
        text-align: center;
        margin-bottom: 30px;
    }
    
    .dash-table-container {
        margin-bottom: 30px;
        background-color: white;
        padding: 15px;
        border-radius: 5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .dash-dropdown {
        width: 50%;
        margin-bottom: 15px;
    }
    
    .dash-graph {
        background-color: white;
        padding: 15px;
        border-radius: 5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    """
    
    with open('assets/style.css', 'w') as f:
        f.write(css_content)

def create_app_js(owner_stats):
    """Create JavaScript file to initialize and display the dashboard"""
    # Convert data to format expected by Dash
    owners = list(owner_stats.keys())
    total_runs = [stats['total_runs'] for stats in owner_stats.values()]
    total_wickets = [stats['total_wickets'] for stats in owner_stats.values()]
    
    # Create DataFrames for tables
    owner_df = {
        'Owner': owners,
        'Total Runs': total_runs,
        'Total Wickets': total_wickets,
        'Player Count': [stats['total_players'] for stats in owner_stats.values()]
    }
    
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
    
    # Create basic JavaScript to initialize the dashboard
    js_content = f"""
    // Cricket Team Owner Statistics Dashboard

    // Load data
    const ownerData = {json.dumps(owner_df)};
    const playerData = {json.dumps(player_data)};
    const ownerNames = {json.dumps(owners)};

    // Initialize after DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {{
        // Create container elements
        const appDiv = document.createElement('div');
        document.getElementById('react-entry-point').innerHTML = '';
        document.getElementById('react-entry-point').appendChild(appDiv);
        
        // Add title
        const title = document.createElement('h1');
        title.textContent = 'Cricket Team Owner Statistics';
        appDiv.appendChild(title);
        
        // Create owner summary section
        const summarySection = document.createElement('div');
        const summaryTitle = document.createElement('h2');
        summaryTitle.textContent = 'Owner Performance Summary';
        summarySection.appendChild(summaryTitle);
        
        // Create owner table
        const ownerTable = document.createElement('table');
        ownerTable.className = 'dash-table';
        
        // Add header
        const tableHeader = document.createElement('thead');
        const headerRow = document.createElement('tr');
        Object.keys(ownerData).forEach(key => {{
            const th = document.createElement('th');
            th.textContent = key;
            headerRow.appendChild(th);
        }});
        tableHeader.appendChild(headerRow);
        ownerTable.appendChild(tableHeader);
        
        // Add rows
        const tableBody = document.createElement('tbody');
        for (let i = 0; i < ownerData.Owner.length; i++) {{
            const row = document.createElement('tr');
            Object.keys(ownerData).forEach(key => {{
                const td = document.createElement('td');
                td.textContent = ownerData[key][i];
                row.appendChild(td);
            }});
            tableBody.appendChild(row);
        }}
        ownerTable.appendChild(tableBody);
        summarySection.appendChild(ownerTable);
        appDiv.appendChild(summarySection);
        
        // Create charts section
        const chartsSection = document.createElement('div');
        chartsSection.style.display = 'flex';
        chartsSection.style.justifyContent = 'space-between';
        
        // Create runs chart
        const runsChartDiv = document.createElement('div');
        runsChartDiv.style.width = '48%';
        const runsTitle = document.createElement('h2');
        runsTitle.textContent = 'Total Runs by Owner';
        runsChartDiv.appendChild(runsTitle);
        const runsChartContainer = document.createElement('div');
        runsChartContainer.id = 'runs-chart';
        runsChartContainer.className = 'dash-graph';
        runsChartDiv.appendChild(runsChartContainer);
        chartsSection.appendChild(runsChartDiv);
        
        // Create wickets chart
        const wicketsChartDiv = document.createElement('div');
        wicketsChartDiv.style.width = '48%';
        const wicketsTitle = document.createElement('h2');
        wicketsTitle.textContent = 'Total Wickets by Owner';
        wicketsChartDiv.appendChild(wicketsTitle);
        const wicketsChartContainer = document.createElement('div');
        wicketsChartContainer.id = 'wickets-chart';
        wicketsChartContainer.className = 'dash-graph';
        wicketsChartDiv.appendChild(wicketsChartContainer);
        chartsSection.appendChild(wicketsChartDiv);
        
        appDiv.appendChild(chartsSection);
        
        // Create player section
        const playerSection = document.createElement('div');
        const playerTitle = document.createElement('h2');
        playerTitle.textContent = 'All Players Data';
        playerSection.appendChild(playerTitle);
        
        // Create player table
        const playerTable = document.createElement('table');
        playerTable.className = 'dash-table';
        
        // Add header
        const playerTableHeader = document.createElement('thead');
        const playerHeaderRow = document.createElement('tr');
        Object.keys(playerData[0]).forEach(key => {{
            const th = document.createElement('th');
            th.textContent = key;
            playerHeaderRow.appendChild(th);
        }});
        playerTableHeader.appendChild(playerHeaderRow);
        playerTable.appendChild(playerTableHeader);
        
        // Add rows
        const playerTableBody = document.createElement('tbody');
        playerData.forEach(player => {{
            const row = document.createElement('tr');
            Object.keys(player).forEach(key => {{
                const td = document.createElement('td');
                td.textContent = player[key];
                row.appendChild(td);
            }});
            playerTableBody.appendChild(row);
        }});
        playerTable.appendChild(playerTableBody);
        playerSection.appendChild(playerTable);
        appDiv.appendChild(playerSection);
        
        // Create player by owner section
        const playerByOwnerSection = document.createElement('div');
        const playerByOwnerTitle = document.createElement('h2');
        playerByOwnerTitle.textContent = 'Player Performance by Owner';
        playerByOwnerSection.appendChild(playerByOwnerTitle);
        
        // Create owner dropdown
        const dropdown = document.createElement('select');
        dropdown.id = 'owner-dropdown';
        dropdown.className = 'dash-dropdown';
        ownerNames.forEach(owner => {{
            const option = document.createElement('option');
            option.value = owner;
            option.textContent = owner;
            dropdown.appendChild(option);
        }});
        playerByOwnerSection.appendChild(dropdown);
        
        // Create chart container
        const ownerPlayersChartContainer = document.createElement('div');
        ownerPlayersChartContainer.id = 'owner-players-chart';
        ownerPlayersChartContainer.className = 'dash-graph';
        playerByOwnerSection.appendChild(ownerPlayersChartContainer);
        appDiv.appendChild(playerByOwnerSection);
        
        // Add footer
        const footer = document.createElement('div');
        const hr = document.createElement('hr');
        footer.appendChild(hr);
        const footerText = document.createElement('p');
        footerText.textContent = 'Cricket Team Owner Statistics Dashboard - Created with Plotly';
        footerText.style.textAlign = 'center';
        footer.appendChild(footerText);
        appDiv.appendChild(footer);
        
        // Initialize Plotly charts
        const runsData = [{{
            x: ownerData.Owner,
            y: ownerData['Total Runs'],
            type: 'bar',
            marker: {{ color: 'rgba(55, 128, 191, 0.7)' }}
        }}];
        
        const wicketsData = [{{
            x: ownerData.Owner,
            y: ownerData['Total Wickets'],
            type: 'bar',
            marker: {{ color: 'rgba(219, 64, 82, 0.7)' }}
        }}];
        
        const runsLayout = {{
            title: 'Total Runs Scored by Each Owner\\'s Players',
            xaxis: {{ title: 'Owner' }},
            yaxis: {{ title: 'Total Runs' }}
        }};
        
        const wicketsLayout = {{
            title: 'Total Wickets Taken by Each Owner\\'s Players',
            xaxis: {{ title: 'Owner' }},
            yaxis: {{ title: 'Total Wickets' }}
        }};
        
        Plotly.newPlot('runs-chart', runsData, runsLayout);
        Plotly.newPlot('wickets-chart', wicketsData, wicketsLayout);
        
        // Initialize player by owner chart
        function updateOwnerPlayersChart() {{
            const selectedOwner = document.getElementById('owner-dropdown').value;
            const filteredPlayers = playerData.filter(player => player.Owner === selectedOwner);
            
            const chartData = [{{
                x: filteredPlayers.map(p => p.Player),
                y: filteredPlayers.map(p => p.Runs),
                type: 'bar',
                marker: {{ color: 'rgba(55, 128, 191, 0.7)' }}
            }}];
            
            const chartLayout = {{
                title: `Runs Scored by ${{selectedOwner}}'s Players`,
                xaxis: {{ title: 'Player' }},
                yaxis: {{ title: 'Runs' }}
            }};
            
            Plotly.newPlot('owner-players-chart', chartData, chartLayout);
        }}
        
        // Add event listener to dropdown
        document.getElementById('owner-dropdown').addEventListener('change', updateOwnerPlayersChart);
        
        // Initialize first chart
        updateOwnerPlayersChart();
    }});
    """
    
    with open('assets/app.js', 'w') as f:
        f.write(js_content)

def main():
    """Main function to build static assets"""
    print("Building static assets for GitHub Pages...")
    
    # Create assets directory
    ensure_dir('assets')
    
    # Load data
    player_teams, team_owners, owner_teams = load_player_team_data()
    player_stats = load_player_stats()
    id_mapping, name_mapping = map_player_ids(player_teams, player_stats)
    owner_stats = calculate_owner_stats(player_teams, player_stats, id_mapping)
    
    # Create CSS file
    create_style_css()
    print("Created style.css")
    
    # Create JavaScript file
    create_app_js(owner_stats)
    print("Created app.js")
    
    # Copy owner_stats.json to assets
    with open('owner_stats.json', 'r') as f:
        owner_data = json.load(f)
    
    with open('assets/owner_stats.json', 'w') as f:
        json.dump(owner_data, f, indent=2)
    print("Copied owner_stats.json to assets")
    
    # Create index.html if it doesn't exist
    if not os.path.exists('index.html'):
        html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Cricket Team Owner Statistics</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <link rel="stylesheet" href="assets/style.css">
</head>
<body>
    <div id="react-entry-point">
        <div class="loading">
            <div class="loading-spinner"></div>
            <div>Loading Cricket Team Owner Statistics...</div>
        </div>
    </div>
    <script src="assets/app.js"></script>
</body>
</html>"""
        
        with open('index.html', 'w') as f:
            f.write(html_content)
        print("Created index.html")
    
    print("\nStatic assets built successfully!")
    print("\nTo deploy to GitHub Pages:")
    print("1. Commit all files to the gh-pages branch")
    print("2. Push to GitHub")
    print("3. Enable GitHub Pages in your repository settings")
    print("4. Access your dashboard at https://[username].github.io/[repository]/")

if __name__ == "__main__":
    main() 