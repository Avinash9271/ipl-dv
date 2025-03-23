# Cricket Team Owner Statistics Dashboard

This dashboard analyzes cricket player statistics and attributes them to team owners, providing insights into owner performance.

## Features

- **Team Owner Summary**: View aggregated statistics for each team owner, including total runs scored and wickets taken.
- **Performance Metrics**: Analyze which owners have the best performing players with metrics like total runs and wickets.
- **Interactive Visualizations**: Explore the data through interactive charts and graphs.
- **Player-Level Details**: Examine detailed statistics for individual players, organized by team owner.

## Local Setup

1. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the dashboard locally:
   ```
   python team_owner_stats.py
   ```

3. Open your web browser and navigate to:
   ```
   http://127.0.0.1:8050/
   ```

## GitHub Pages Deployment

This dashboard is designed to work with GitHub Pages. To deploy:

1. Fork or clone this repository to your GitHub account.

2. Create a new branch called `gh-pages`:
   ```
   git checkout -b gh-pages
   ```

3. Create an `index.html` file in the root directory that will serve the dashboard:
   ```html
   <!DOCTYPE html>
   <html>
   <head>
       <title>Cricket Team Owner Statistics</title>
       <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
       <script src="https://unpkg.com/dash-renderer/dash_renderer/dash_renderer.js"></script>
       <script src="https://unpkg.com/dash-core-components/dash_core_components/dash_core_components.js"></script>
       <script src="https://unpkg.com/dash-html-components/dash_html_components/dash_html_components.js"></script>
       <script src="https://unpkg.com/dash-table/dash_table/dash_table.js"></script>
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
   </html>
   ```

4. Create an `assets` folder with:
   - `app.js` - Compiled dashboard JavaScript
   - `style.css` - Dashboard styles
   - Data files (owner_stats.json)

5. Run the following command to generate static assets:
   ```
   python build_static.py
   ```

6. Push your changes to GitHub:
   ```
   git add .
   git commit -m "Add GitHub Pages deployment"
   git push origin gh-pages
   ```

7. Go to your repository settings and enable GitHub Pages for the `gh-pages` branch.

8. Your dashboard will be available at: `https://[your-username].github.io/[repository-name]/`

## How It Works

The system processes two main data sources:

1. **teams.csv**: Contains the mapping between players, teams, and owners.
2. **player_stats.json**: Contains statistical data for players from matches.

The script performs the following operations:
- Loads and processes player-team-owner relationships
- Loads player statistics from the JSON file
- Maps player IDs between the two datasets
- Calculates aggregated statistics for each team owner
- Generates a dashboard to visualize the data

## Dashboard Components

1. **Owner Performance Summary Table**: Shows key metrics for each owner.
2. **Total Runs Chart**: Bar chart showing total runs scored by each owner's players.
3. **Total Wickets Chart**: Bar chart showing wickets taken by each owner's players.
4. **All Players Table**: Detailed table with player-level information.
5. **Player Performance by Owner**: Interactive chart allowing you to select an owner and view their players' performances.

## Data Structure

The calculated owner statistics are saved to `owner_stats.json` with the following structure:

```json
{
  "Owner Name": {
    "total_runs": 123,
    "total_wickets": 5,
    "total_players": 3,
    "players": [
      {
        "player_id": "123",
        "player_name": "Player Name",
        "team_id": 42,
        "runs": 60,
        "wickets": 2
      },
      ...
    ]
  },
  ...
}
``` 