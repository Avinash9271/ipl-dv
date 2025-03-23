# Cricket Team Owner Statistics Dashboard

A interactive dashboard to analyze cricket player statistics and attribute them to team owners.

## Features

- **Team Owner Summary**: View aggregated statistics for each team owner, including total runs scored and wickets taken.
- **Performance Metrics**: Analyze which owners have the best performing players.
- **Interactive Visualizations**: Explore the data through interactive charts and graphs.
- **Player-Level Details**: Examine detailed statistics for individual players, organized by team owner.

## Demo

View the live dashboard at: [GitHub Pages Demo](https://[your-username].github.io/[repository-name]/)

## Local Setup

1. Clone this repository:
   ```
   git clone https://github.com/[your-username]/[repository-name].git
   cd [repository-name]
   ```

2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the dashboard locally:
   ```
   python team_owner_stats.py
   ```

4. Open your web browser and navigate to:
   ```
   http://127.0.0.1:8050/
   ```

## GitHub Pages Deployment

This dashboard can be deployed to GitHub Pages for free hosting:

1. Fork or clone this repository to your GitHub account.

2. Create a new branch called `gh-pages`:
   ```
   git checkout -b gh-pages
   ```

3. Generate the static assets:
   ```
   python build_static.py
   ```

4. Push your changes to GitHub:
   ```
   git add .
   git commit -m "Add GitHub Pages deployment"
   git push origin gh-pages
   ```

5. Go to your repository settings and enable GitHub Pages for the `gh-pages` branch.

6. Your dashboard will be available at: `https://[your-username].github.io/[repository-name]/`

## Data Sources

The dashboard processes two main data sources:

1. **teams.csv**: Contains the mapping between players, teams, and owners.
2. **player_stats.json**: Contains statistical data for players from matches.

## How It Works

The system performs the following operations:
- Loads and processes player-team-owner relationships
- Loads player statistics from the JSON file
- Maps player IDs between the two datasets
- Calculates aggregated statistics for each team owner
- Generates a dashboard to visualize the data

For more detailed information, see [TEAM_STATS_README.md](TEAM_STATS_README.md). 