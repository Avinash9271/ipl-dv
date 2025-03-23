#!/usr/bin/env python3
"""
Cricket Stats Admin Dashboard
Admin interface for managing cricket match data and API queries.
"""

import os
import json
import dash
from dash import dcc, html, dash_table, callback, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
from api_client import CricAPIClient
from stats_processor import StatsProcessor
from pathlib import Path
import datetime
import time

# Constants
PROCESSED_MATCHES_FILE = "processed_matches.json"
MATCH_DATA_DIR = "match_data"
PLAYER_STATS_FILE = "player_stats.json"
DEFAULT_API_KEY = os.environ.get("CRIC_API_KEY", "")

# Ensure directories exist
Path(MATCH_DATA_DIR).mkdir(exist_ok=True)

# Get processed matches
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

# Save processed match
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

# Initialize the API client
def get_api_client(api_key):
    """Create API client with the provided key"""
    return CricAPIClient(api_key)

# Secure the API key display
def mask_api_key(api_key):
    """Return a masked version of the API key"""
    if not api_key:
        return ""
    return "•" * (len(api_key) - 4) + api_key[-4:]

# Initialize Dash app
app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

app.title = "Cricket Stats Admin Dashboard"

# Define the layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Cricket Stats Admin Dashboard", className="mt-4 mb-4 text-center")
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("API Settings"),
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("API Key (last 4 digits shown)"),
                            dbc.InputGroup([
                                dbc.Input(
                                    id="api-key-input",
                                    type="password",
                                    placeholder="Enter API Key",
                                    value=DEFAULT_API_KEY
                                ),
                                dbc.InputGroupText(id="api-key-display")
                            ]),
                        ], width=6),
                        dbc.Col([
                            html.Label("Series ID"),
                            dbc.Input(
                                id="series-id-input",
                                type="text",
                                placeholder="Enter Series ID"
                            ),
                            dbc.Button(
                                "Fetch Series Info", 
                                id="fetch-series-btn", 
                                color="primary", 
                                className="mt-2"
                            ),
                        ], width=6)
                    ]),
                    html.Div(id="api-status", className="mt-3")
                ])
            ], className="mb-4")
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Series Information"),
                dbc.CardBody([
                    html.Div(id="series-info"),
                    dbc.Button(
                        "Refresh Matches", 
                        id="refresh-matches-btn", 
                        color="success", 
                        className="mt-3",
                        style={"display": "none"}
                    ),
                ])
            ], className="mb-4")
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Matches"),
                dbc.CardBody([
                    html.Div(id="matches-table-container"),
                ])
            ], className="mb-4")
        ])
    ]),
    
    # Status modal for showing processing status
    dbc.Modal([
        dbc.ModalHeader("Processing"),
        dbc.ModalBody(id="modal-content"),
        dbc.ModalFooter(
            dbc.Button("Close", id="close-modal", className="ml-auto")
        ),
    ], id="status-modal"),
    
    # Store component to maintain state
    dcc.Store(id="series-data-store"),
    dcc.Store(id="matches-data-store"),
    dcc.Store(id="processed-info-store"),
    
    # Interval for updates
    dcc.Interval(
        id="interval-component",
        interval=10*1000,  # 10 seconds in milliseconds
        n_intervals=0,
        disabled=True
    ),
    
    # Hidden div for tracking processing state
    html.Div(id="processing-state", style={"display": "none"})
])

# Callback for API key display
@app.callback(
    Output("api-key-display", "children"),
    Input("api-key-input", "value")
)
def update_api_key_display(api_key):
    return mask_api_key(api_key)

# Callback for fetching series info
@app.callback(
    [
        Output("api-status", "children"),
        Output("series-info", "children"),
        Output("series-data-store", "data"),
        Output("refresh-matches-btn", "style")
    ],
    Input("fetch-series-btn", "n_clicks"),
    [
        State("api-key-input", "value"),
        State("series-id-input", "value")
    ],
    prevent_initial_call=True
)
def fetch_series_info(n_clicks, api_key, series_id):
    if not n_clicks:
        return "", "", None, {"display": "none"}
    
    if not api_key:
        return dbc.Alert("Please enter an API Key", color="danger"), "", None, {"display": "none"}
    
    client = get_api_client(api_key)
    
    # Set environment variable for the API key
    os.environ["CRICAPI_KEY"] = api_key
    
    # If series_id is provided, set it as environment variable
    if series_id:
        os.environ["SERIES_ID"] = series_id
    
    try:
        series = client.get_series()
        if not series:
            return dbc.Alert("Failed to fetch series information", color="danger"), "", None, {"display": "none"}
        
        # Create a card with series information
        series_info = dbc.Card([
            dbc.CardBody([
                html.H5(series["info"]["name"], className="card-title"),
                html.P(f"Series ID: {series['id']}", className="card-text"),
                html.P(f"Start Date: {series['info'].get('startDate', 'N/A')}", className="card-text"),
                html.P(f"End Date: {series['info'].get('endDate', 'N/A')}", className="card-text"),
                html.P(f"ODI: {series['info'].get('odi', False)}", className="card-text"),
                html.P(f"T20: {series['info'].get('t20', False)}", className="card-text"),
                html.P(f"Test: {series['info'].get('test', False)}", className="card-text"),
                html.P(f"Squads: {series['info'].get('squads', False)}", className="card-text"),
                html.P(f"Matches: {series['info'].get('matches', False)}", className="card-text")
            ])
        ])
        
        return (
            dbc.Alert("Successfully fetched series information", color="success"),
            series_info,
            series,
            {"display": "block"}
        )
    except Exception as e:
        return dbc.Alert(f"Error: {str(e)}", color="danger"), "", None, {"display": "none"}

# Callback for refreshing matches
@app.callback(
    [
        Output("matches-table-container", "children"),
        Output("matches-data-store", "data"),
        Output("processed-info-store", "data")
    ],
    Input("refresh-matches-btn", "n_clicks"),
    [
        State("api-key-input", "value"),
        State("series-data-store", "data")
    ],
    prevent_initial_call=True
)
def refresh_matches(n_clicks, api_key, series_data):
    if not n_clicks or not api_key or not series_data:
        return "", None, None
    
    client = get_api_client(api_key)
    
    try:
        # Get all matches for the series
        series_id = series_data.get("id")
        matches = client.get_all_matches(series_id)
        
        if not matches:
            return dbc.Alert("No matches found for this series", color="warning"), None, None
        
        # Get processed matches
        processed_matches = get_processed_matches()
        
        # Prepare data for the table
        matches_data = []
        for match in matches:
            match_id = match.get("id")
            match_status = match.get("status")
            match_name = match.get("name", "Unknown")
            match_date = match.get("date", "Unknown")
            
            # Check if match is processed
            is_processed = match_id in processed_matches
            processed_at = processed_matches.get(match_id, {}).get("processed_at", "N/A")
            
            matches_data.append({
                "id": match_id,
                "name": match_name,
                "date": match_date,
                "status": match_status,
                "processed": "Yes" if is_processed else "No",
                "processed_at": processed_at if is_processed else "N/A"
            })
        
        # Create the matches table
        matches_table = dash_table.DataTable(
            id="matches-table",
            columns=[
                {"name": "ID", "id": "id"},
                {"name": "Name", "id": "name"},
                {"name": "Date", "id": "date"},
                {"name": "Status", "id": "status"},
                {"name": "Processed", "id": "processed"},
                {"name": "Processed At", "id": "processed_at"}
            ],
            data=matches_data,
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left"},
            style_header={
                "backgroundColor": "rgb(230, 230, 230)",
                "fontWeight": "bold"
            },
            style_data_conditional=[
                {
                    "if": {"filter_query": "{processed} = 'Yes'"},
                    "backgroundColor": "rgba(0, 255, 0, 0.1)"
                }
            ],
            row_selectable="multi",
            selected_rows=[],
            page_size=10
        )
        
        # Add a button to process selected matches
        matches_container = html.Div([
            matches_table,
            dbc.Button(
                "Process Selected Matches", 
                id="process-matches-btn", 
                color="primary", 
                className="mt-3"
            ),
            dbc.Button(
                "Reprocess All Completed Matches", 
                id="reprocess-all-btn", 
                color="warning", 
                className="mt-3 ml-2"
            ),
            html.Div(id="processing-status", className="mt-3")
        ])
        
        return matches_container, matches_data, processed_matches
    except Exception as e:
        return dbc.Alert(f"Error: {str(e)}", color="danger"), None, None

# Callback for processing selected matches
@app.callback(
    [
        Output("status-modal", "is_open"),
        Output("modal-content", "children"),
        Output("interval-component", "disabled"),
        Output("processing-state", "children")
    ],
    [
        Input("process-matches-btn", "n_clicks"),
        Input("reprocess-all-btn", "n_clicks"),
        Input("close-modal", "n_clicks"),
        Input("interval-component", "n_intervals")
    ],
    [
        State("matches-table", "selected_rows"),
        State("matches-data-store", "data"),
        State("api-key-input", "value"),
        State("status-modal", "is_open"),
        State("processing-state", "children")
    ],
    prevent_initial_call=True
)
def process_matches(process_clicks, reprocess_clicks, close_clicks, n_intervals, 
                   selected_rows, matches_data, api_key, is_open, processing_state):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    # Closing the modal
    if trigger_id == "close-modal":
        return False, "", True, ""
    
    # Interval tick for updating processing status
    if trigger_id == "interval-component":
        if processing_state:
            current_state = json.loads(processing_state)
            if current_state["status"] == "completed":
                return False, "", True, ""
            
            log_file = current_state.get("log_file")
            logs = []
            
            if log_file and os.path.exists(log_file):
                with open(log_file, "r") as f:
                    logs = f.readlines()[-20:]  # Show last 20 lines
            
            return is_open, html.Pre("\n".join(logs)), False, processing_state
        return False, "", True, ""
    
    # Initial processing request
    if not matches_data:
        return is_open, "No matches data available", True, ""
    
    # Handle reprocess all
    if trigger_id == "reprocess-all-btn" and reprocess_clicks:
        selected_matches = [
            match for match in matches_data 
            if match["status"] == "completed"
        ]
    # Handle process selected
    elif trigger_id == "process-matches-btn" and process_clicks and selected_rows:
        selected_matches = [matches_data[idx] for idx in selected_rows]
    else:
        return is_open, "", True, ""
    
    if not selected_matches:
        return True, "No matches selected for processing", True, ""
    
    # Set up processing
    log_file = f"processing_{int(time.time())}.log"
    
    # Prepare initial state
    process_state = {
        "status": "processing",
        "matches": [match["id"] for match in selected_matches],
        "log_file": log_file,
        "current": 0,
        "total": len(selected_matches)
    }
    
    with open(log_file, "w") as f:
        f.write(f"Starting processing of {len(selected_matches)} matches\n")
    
    # Start processing in a separate thread or process
    import threading
    
    def process_matches_thread():
        client = get_api_client(api_key)
        processor = StatsProcessor(client)
        
        with open(log_file, "a") as f:
            f.write(f"Initialized API client and StatsProcessor\n")
            
            for i, match in enumerate(selected_matches):
                match_id = match["id"]
                match_name = match["name"]
                
                f.write(f"\nProcessing match {i+1}/{len(selected_matches)}: {match_name} ({match_id})\n")
                
                try:
                    # Get match details
                    match_details = client.get_match_details(match_id)
                    
                    if match_details:
                        # Process ball-by-ball data
                        if processor._process_match_data(match_id, match_details):
                            f.write(f"Successfully processed ball-by-ball data for match {match_id}\n")
                            save_processed_match(match_id, match)
                        else:
                            f.write(f"No ball-by-ball data available for match {match_id}\n")
                    else:
                        f.write(f"Failed to fetch details for match {match_id}\n")
                except Exception as e:
                    f.write(f"Error processing match {match_id}: {str(e)}\n")
            
            # Save the results
            if processor.player_stats:
                processor.save_to_csv()
                processor.save_to_json()
                f.write("\nPlayer statistics saved to CSV and JSON files\n")
            else:
                f.write("\nNo player statistics were generated\n")
            
            f.write("\nProcessing completed\n")
            
            # Update process state
            process_state["status"] = "completed"
            with open(log_file, "a") as f:
                f.write("Processing thread finished\n")
    
    # Start processing thread
    thread = threading.Thread(target=process_matches_thread)
    thread.daemon = True
    thread.start()
    
    return True, f"Started processing {len(selected_matches)} matches...", False, json.dumps(process_state)

# Callback to update the processing status
@app.callback(
    Output("processing-status", "children"),
    [Input("process-matches-btn", "n_clicks"),
     Input("reprocess-all-btn", "n_clicks")],
    prevent_initial_call=True
)
def update_processing_status(process_clicks, reprocess_clicks):
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if trigger_id == "process-matches-btn" and process_clicks:
        return dbc.Alert("Processing selected matches. See modal for details.", color="info")
    elif trigger_id == "reprocess-all-btn" and reprocess_clicks:
        return dbc.Alert("Reprocessing all completed matches. See modal for details.", color="info")
    
    return ""

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True) 