# Cricket Team Owner Statistics Dashboard

A interactive dashboard to analyze cricket player statistics and attribute them to team owners.

## Features

- **Live Data Processing**: Fetches cricket match data directly from CricAPI and processes it in real-time.
- **Team Owner Summary**: View aggregated statistics for each team owner, including total score based on player performance.
- **Performance Metrics**: Analyze which owners have the best performing players with detailed scoring breakdown.
- **Player-Level Details**: Examine detailed statistics for individual players, organized by team owner.
- **Scoring System**: Uses a comprehensive scoring system that rewards batting, bowling, and fielding performances.

## Demo

View the live dashboard at: [GitHub Pages Demo](https://avinash9271.github.io/ipl-dv/)

## Scoring System

The dashboard uses the following scoring system to evaluate player performances:

- **Base Score**: Each player starts with 4 points
- **Batting**: 
  - 1 point per run
  - 8 bonus points for reaching 50 runs
  - 8 additional bonus points for reaching 100 runs
- **Bowling**:
  - 20 points for each "good" wicket (bowled, LBW, caught & bowled)
  - 16 points for other wickets
  - 15 bonus points for taking 3 or more wickets
- **Fielding**:
  - 8 points for each catch
  - 8 points for each run out
- **Highest Scorer Bonus**: The highest scoring player in each match gets a 1.3x multiplier

## Local Setup

1. Clone this repository:
   ```
   git clone https://github.com/Avinash9271/ipl-dv.git
   cd ipl-dv
   ```

2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the cricket scorer script with your API key:
   ```
   python cricket_scorer.py YOUR_API_KEY
   ```
   
   Alternatively, set the API key as an environment variable:
   ```
   export CRICAPI_KEY=YOUR_API_KEY
   python cricket_scorer.py
   ```

4. For the admin dashboard (optional):
   ```
   python admin_dashboard.py
   ```
   
   Then open your web browser and navigate to:
   ```
   http://127.0.0.1:8050/
   ```

## GitHub Pages Deployment

The static HTML dashboard is available on GitHub Pages. To use it:

1. Visit [https://avinash9271.github.io/ipl-dv/](https://avinash9271.github.io/ipl-dv/)
2. Enter your CricAPI key in the form or include it as a URL parameter: `?key=YOUR_API_KEY`

Note: The GitHub Pages version does not run the Python script directly. For full functionality, run the script locally as described above.

## Data Sources

The system uses two main data sources:

1. **teams.csv**: Contains the mapping between players, teams, and owners.
2. **CricAPI**: Fetches live cricket match data using the CricAPI service.

## How It Works

The system performs the following operations:
- Loads team-owner relationships from teams.csv
- Fetches match data directly from CricAPI
- Processes ball-by-ball data to calculate player statistics
- Applies the scoring system to evaluate player performances
- Aggregates statistics by team owner
- Displays the results in a tabular format 