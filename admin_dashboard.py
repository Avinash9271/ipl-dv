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
    if not n_clicks or not series_data:
        return "", None, None
    
    client = get_api_client(api_key)
    processed_matches = get_processed_matches()
    
    try:
        matches = client.get_matches()
        if not matches:
            return dbc.Alert("No matches found", color="warning"), None, None
        
        # Create DataFrame for display
        matches_data = []
        for match in matches:
            match_id = match["id"]
            processed_info = processed_matches.get(match_id, {})
            
            matches_data.append({
                "id": match_id,
                "name": match.get("name", "Unknown"),
                "status": match.get("status", "Unknown"),
                "date": match.get("date", "Unknown"),
                "processed": "Yes" if match_id in processed_matches else "No",
                "processed_at": processed_info.get("processed_at", "Never")
            })
        
        df = pd.DataFrame(matches_data)
        
        # Create table
        table = dash_table.DataTable(
            id="matches-table",
            columns=[
                {"name": "Match", "id": "name"},
                {"name": "Status", "id": "status"},
                {"name": "Date", "id": "date"},
                {"name": "Processed", "id": "processed"},
                {"name": "Last Processed", "id": "processed_at"}
            ],
            data=df.to_dict("records"),
            style_table={"overflowX": "auto"},
            style_cell={
                "textAlign": "left",
                "padding": "10px"
            },
            style_header={
                "backgroundColor": "rgb(230, 230, 230)",
                "fontWeight": "bold"
            },
            row_selectable="multi",
            selected_rows=[],
            page_size=10
        )
        
        # Add process buttons
        buttons = html.Div([
            dbc.Button(
                "Process Selected",
                id="process-matches-btn",
                color="primary",
                className="me-2"
            ),
            dbc.Button(
                "Reprocess All",
                id="reprocess-all-btn",
                color="warning"
            )
        ], className="mt-3")
        
        return [table, buttons], matches_data, processed_matches
    except Exception as e:
        return dbc.Alert(f"Error: {str(e)}", color="danger"), None, None

# Callback for processing matches
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
    if not ctx.triggered:
        return False, "", True, ""
    
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if trigger_id == "close-modal":
        return False, "", True, ""
    
    if trigger_id == "interval-component":
        if not processing_state:
            return False, "", True, ""
        return True, processing_state, False, processing_state
    
    if not matches_data:
        return False, "", True, ""
    
    # Get matches to process
    matches_to_process = []
    if trigger_id == "process-matches-btn":
        if not selected_rows:
            return False, "Please select matches to process", True, ""
        matches_to_process = [matches_data[i] for i in selected_rows]
    elif trigger_id == "reprocess-all-btn":
        matches_to_process = matches_data
    
    if not matches_to_process:
        return False, "No matches to process", True, ""
    
    # Initialize processing
    client = get_api_client(api_key)
    processor = StatsProcessor()
    
    def process_matches_thread():
        nonlocal processing_state
        try:
            for i, match in enumerate(matches_to_process, 1):
                match_id = match["id"]
                processing_state = f"Processing match {i}/{len(matches_to_process)}: {match['name']}"
                
                # Get match details
                match_details = client.get_match_details(match_id)
                if not match_details:
                    continue
                
                # Process match
                processor.process_match(match_details)
                
                # Save as processed
                save_processed_match(match_id, match)
            
            processing_state = "Processing completed successfully!"
        except Exception as e:
            processing_state = f"Error during processing: {str(e)}"
    
    # Start processing thread
    import threading
    thread = threading.Thread(target=process_matches_thread)
    thread.start()
    
    return True, "Starting processing...", False, "Starting processing..."

# Callback for updating processing status
@app.callback(
    Output("processing-status", "children"),
    [Input("process-matches-btn", "n_clicks"),
     Input("reprocess-all-btn", "n_clicks")],
    prevent_initial_call=True
)
def update_processing_status(process_clicks, reprocess_clicks):
    return "Processing..."

if __name__ == "__main__":
    app.run(debug=True) 