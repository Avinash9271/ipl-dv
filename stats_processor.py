import pandas as pd
import json
from datetime import datetime
from collections import defaultdict
import csv

class StatsProcessor:
    """Process cricket match data to generate player statistics"""
    
    def __init__(self, api_client=None):
        self.player_stats = {}
        self.api_client = api_client
        self.processed_matches = []  # Track processed match IDs
        self.match_player_stats = defaultdict(dict)  # Track player stats by match
    
    def process_all_matches(self, matches):
        """Process all matches and calculate player statistics"""
        total_matches = len(matches)
        successful_count = 0
        ball_by_ball_count = 0
        
        print(f"Processing {total_matches} matches...")
        
        for idx, match in enumerate(matches, 1):
            match_id = match.get('id')
            match_name = match.get('name', 'Unknown Match')
            
            print(f"Processing match {idx}/{total_matches}: {match_name}")
            
            # If we have the API client, fetch the match details
            if self.api_client and match_id:
                match_details = self.api_client.get_match_details(match_id)
                if match_details:
                    # Process ball-by-ball data if available
                    if self._process_match_data(match_id, match_details):
                        successful_count += 1
                        ball_by_ball_count += 1
                        if match_id not in self.processed_matches:
                            self.processed_matches.append(match_id)
                        
                        # Calculate player scores for this match
                        self.calculate_player_scores(match_id)
                    else:
                        print(f"  No ball-by-ball data available for match {match_id}")
                else:
                    print(f"  Failed to fetch details for match {match_id}")
            else:
                # Process the match data directly if API client is not provided
                if self._process_match_data(match_id, match):
                    successful_count += 1
                    ball_by_ball_count += 1
                    if match_id not in self.processed_matches:
                        self.processed_matches.append(match_id)
                        
                    # Calculate player scores for this match
                    self.calculate_player_scores(match_id)
                else:
                    print(f"  No ball-by-ball data available for match {match_id}")
        
        # After processing all matches, save the results
        if self.player_stats:
            self.save_to_csv()
            self.save_to_json()
        
        print(f"\nSummary:")
        print(f"  Total matches processed: {total_matches}")
        print(f"  Matches with ball-by-ball data: {ball_by_ball_count}")
        print(f"  Total players with statistics: {len(self.player_stats)}")
        
        return successful_count
    
    def _process_match_data(self, match_id, match_data):
        """Process ball-by-ball data from a match and update player statistics"""
        has_ball_data = False
        
        # Initialize match-specific player stats
        self.match_player_stats[match_id] = {}
        
        # Extract ball-by-ball data
        data = match_data.get('data', match_data)
        
        # Try to extract ball-by-ball data from different possible locations
        ball_by_ball = data.get('ballByBall', [])
        if not ball_by_ball and 'bbb' in data:
            ball_by_ball = data.get('bbb', [])
        
        if not ball_by_ball:
            return False
        
        # If ballByBall is a list of innings
        if isinstance(ball_by_ball, list):
            # Check if the format is innings data with overs
            innings_data = []
            for inning in ball_by_ball:
                if isinstance(inning, dict) and 'overs' in inning:
                    innings_data.append(inning)
                    has_ball_data = True
            
            if has_ball_data:
                # Process each innings
                for inning in innings_data:
                    batting_team = inning.get('battingTeam', {}).get('name', 'Unknown Team')
                    bowling_team = inning.get('bowlingTeam', {}).get('name', 'Unknown Team')
                    
                    # Process overs
                    for over in inning.get('overs', []):
                        # Process each ball
                        for ball in over.get('balls', []):
                            self._process_ball(match_id, ball, batting_team, bowling_team)
            else:
                # Otherwise, assume it's a flat list of balls
                for ball in ball_by_ball:
                    self._process_ball(match_id, ball, 'Unknown Team', 'Unknown Team')
                has_ball_data = True
        
        return has_ball_data
    
    def _process_ball(self, match_id, ball, batting_team, bowling_team):
        """Process a single ball's data"""
        # Extract player data
        batter = ball.get('batter', {}) or ball.get('batsman', {})
        bowler = ball.get('bowler', {})
        
        batter_id = batter.get('id')
        batter_name = batter.get('name', 'Unknown Batter')
        bowler_id = bowler.get('id')
        bowler_name = bowler.get('name', 'Unknown Bowler')
        
        # Skip if no player IDs
        if not batter_id or not bowler_id:
            return
        
        # Initialize match-specific player stats if needed
        for player_id, name in [(batter_id, batter_name), (bowler_id, bowler_name)]:
            if player_id not in self.match_player_stats[match_id]:
                self.match_player_stats[match_id][player_id] = {
                    'name': name,
                    'runs': 0,
                    'balls': 0,
                    'bowled_balls': 0,
                    'conceded': 0,
                    'wickets': 0,
                    'good_one': 0,
                    'dots': 0,
                    'catches': 0,
                    'run_outs': 0,
                    'score': 0  # Player's score according to the scoring system
                }
        
        # Initialize player entries if needed
        for player_id, name, team in [(batter_id, batter_name, batting_team), (bowler_id, bowler_name, bowling_team)]:
            if player_id not in self.player_stats:
                self.player_stats[player_id] = {
                    'name': name,
                    'team': team,
                    'matches': 1,
                    'match_scores': {},  # Track scores by match
                    'total_score': 0,    # Sum of all match scores
                    'batting': {
                        'runs': 0,
                        'balls_faced': 0,
                        'fours': 0,
                        'sixes': 0,
                        'dismissals': 0,
                        'dismissal_types': {}
                    },
                    'bowling': {
                        'balls_bowled': 0,
                        'runs_conceded': 0,
                        'wickets': 0,
                        'wicket_types': {},
                        'good_ones': 0,
                        'dots': 0
                    },
                    'fielding': {
                        'catches': 0,
                        'run_outs': 0
                    }
                }
            elif match_id not in self.processed_matches:
                # If player already exists but this is a new match
                self.player_stats[player_id]['matches'] += 1
        
        # Get the outcome of the ball
        runs_info = ball.get('runs', {})
        if isinstance(runs_info, dict):
            runs_batter = runs_info.get('batter', 0)
            runs_extras = runs_info.get('extras', 0)
            runs_total = runs_info.get('total', 0)
        else:
            # Handle the case where runs might be a direct integer
            runs_batter = runs_info
            runs_extras = ball.get('extras', 0)
            runs_total = runs_batter + runs_extras
        
        # Update batter stats
        batting_stats = self.player_stats[batter_id]['batting']
        batting_stats['runs'] += runs_batter
        batting_stats['balls_faced'] += 1
        
        # Update match-specific batter stats
        match_batter_stats = self.match_player_stats[match_id][batter_id]
        match_batter_stats['runs'] += runs_batter
        match_batter_stats['balls'] += 1
        
        if runs_batter == 4:
            batting_stats['fours'] += 1
        elif runs_batter == 6:
            batting_stats['sixes'] += 1
        
        # Update bowler stats
        bowling_stats = self.player_stats[bowler_id]['bowling']
        bowling_stats['balls_bowled'] += 1
        bowling_stats['runs_conceded'] += runs_total
        
        # Update match-specific bowler stats
        match_bowler_stats = self.match_player_stats[match_id][bowler_id]
        match_bowler_stats['bowled_balls'] += 1
        match_bowler_stats['conceded'] += runs_total
        
        # Check for dot ball (no runs)
        if runs_total == 0:
            bowling_stats['dots'] += 1
            match_bowler_stats['dots'] += 1
        
        # Handle wickets
        is_wicket = ball.get('isWicket', False)
        if is_wicket:
            wicket = ball.get('wicket', {})
            wicket_type = wicket.get('type', 'Unknown')
            dismissed_player = wicket.get('playerOut', {})
            dismissed_batter_id = dismissed_player.get('id')
            
            # Update bowler wicket count if it's a bowler wicket
            if wicket_type in ['bowled', 'caught', 'lbw', 'stumped', 'caught and bowled', 'hit wicket']:
                bowling_stats['wickets'] += 1
                match_bowler_stats['wickets'] += 1
                
                # Count as a "good one" only for specific wicket types
                if wicket_type in ['bowled', 'lbw', 'caught and bowled']:
                    bowling_stats['good_ones'] += 1
                    match_bowler_stats['good_one'] += 1
                
                if wicket_type not in bowling_stats['wicket_types']:
                    bowling_stats['wicket_types'][wicket_type] = 0
                bowling_stats['wicket_types'][wicket_type] += 1
            
            # Update fielding stats for catch
            if wicket_type == 'caught':
                fielder = wicket.get('fielders', [{}])[0] if wicket.get('fielders') else {}
                fielder_id = fielder.get('id')
                
                if fielder_id:
                    # Initialize fielder entry if needed
                    if fielder_id not in self.player_stats:
                        fielder_name = fielder.get('name', 'Unknown Fielder')
                        self.player_stats[fielder_id] = {
                            'name': fielder_name,
                            'team': bowling_team,
                            'matches': 1,
                            'match_scores': {},
                            'total_score': 0,
                            'batting': {
                                'runs': 0,
                                'balls_faced': 0,
                                'fours': 0,
                                'sixes': 0,
                                'dismissals': 0,
                                'dismissal_types': {}
                            },
                            'bowling': {
                                'balls_bowled': 0,
                                'runs_conceded': 0,
                                'wickets': 0,
                                'wicket_types': {},
                                'good_ones': 0,
                                'dots': 0
                            },
                            'fielding': {
                                'catches': 0,
                                'run_outs': 0
                            }
                        }
                    
                    # Update catches count
                    if 'fielding' not in self.player_stats[fielder_id]:
                        self.player_stats[fielder_id]['fielding'] = {'catches': 0, 'run_outs': 0}
                    
                    self.player_stats[fielder_id]['fielding']['catches'] += 1
                    
                    # Update match-specific fielder stats
                    if fielder_id not in self.match_player_stats[match_id]:
                        self.match_player_stats[match_id][fielder_id] = {
                            'name': fielder.get('name', 'Unknown Fielder'),
                            'runs': 0,
                            'balls': 0,
                            'bowled_balls': 0,
                            'conceded': 0,
                            'wickets': 0,
                            'good_one': 0,
                            'dots': 0,
                            'catches': 0,
                            'run_outs': 0,
                            'score': 0
                        }
                    
                    self.match_player_stats[match_id][fielder_id]['catches'] += 1
            
            # Handle run outs
            elif wicket_type == 'run out':
                fielders = wicket.get('fielders', [])
                for fielder in fielders:
                    fielder_id = fielder.get('id')
                    
                    if fielder_id:
                        # Initialize fielder entry if needed
                        if fielder_id not in self.player_stats:
                            fielder_name = fielder.get('name', 'Unknown Fielder')
                            self.player_stats[fielder_id] = {
                                'name': fielder_name,
                                'team': bowling_team,
                                'matches': 1,
                                'match_scores': {},
                                'total_score': 0,
                                'batting': {
                                    'runs': 0,
                                    'balls_faced': 0,
                                    'fours': 0,
                                    'sixes': 0,
                                    'dismissals': 0,
                                    'dismissal_types': {}
                                },
                                'bowling': {
                                    'balls_bowled': 0,
                                    'runs_conceded': 0,
                                    'wickets': 0,
                                    'wicket_types': {},
                                    'good_ones': 0,
                                    'dots': 0
                                },
                                'fielding': {
                                    'catches': 0,
                                    'run_outs': 0
                                }
                            }
                        
                        # Update run outs count
                        if 'fielding' not in self.player_stats[fielder_id]:
                            self.player_stats[fielder_id]['fielding'] = {'catches': 0, 'run_outs': 0}
                        
                        self.player_stats[fielder_id]['fielding']['run_outs'] += 1
                        
                        # Update match-specific fielder stats
                        if fielder_id not in self.match_player_stats[match_id]:
                            self.match_player_stats[match_id][fielder_id] = {
                                'name': fielder.get('name', 'Unknown Fielder'),
                                'runs': 0,
                                'balls': 0,
                                'bowled_balls': 0,
                                'conceded': 0,
                                'wickets': 0,
                                'good_one': 0,
                                'dots': 0,
                                'catches': 0,
                                'run_outs': 0,
                                'score': 0
                            }
                        
                        self.match_player_stats[match_id][fielder_id]['run_outs'] += 1
            
            # Update dismissed batter stats
            if dismissed_batter_id and dismissed_batter_id in self.player_stats:
                dismissed_stats = self.player_stats[dismissed_batter_id]['batting']
                dismissed_stats['dismissals'] += 1
                if wicket_type not in dismissed_stats['dismissal_types']:
                    dismissed_stats['dismissal_types'][wicket_type] = 0
                dismissed_stats['dismissal_types'][wicket_type] += 1
    
    def calculate_player_scores(self, match_id):
        """Calculate player scores for a specific match using the scoring system"""
        if match_id not in self.match_player_stats:
            return
        
        # Calculate score for each player in the match
        for player_id, stats in self.match_player_stats[match_id].items():
            # Calculate score using the provided formula
            score = self.get_score(stats)
            
            # Save the score to the match player stats
            self.match_player_stats[match_id][player_id]['score'] = score
        
        # Find the highest scoring player
        max_score = 0
        max_score_player_id = None
        
        for player_id, stats in self.match_player_stats[match_id].items():
            if stats['score'] > max_score:
                max_score = stats['score']
                max_score_player_id = player_id
        
        # Apply 1.3x multiplier to the highest scoring player
        if max_score_player_id:
            player_stats = self.match_player_stats[match_id][max_score_player_id]
            original_score = player_stats['score']
            player_stats['score'] = original_score * 1.3
            
            print(f"  Applied 1.3x multiplier to {player_stats['name']} (Score: {original_score:.2f} -> {player_stats['score']:.2f})")
        
        # Update the main player_stats with match scores
        for player_id, stats in self.match_player_stats[match_id].items():
            score = stats['score']
            
            # Add score to player's match scores
            if player_id in self.player_stats:
                self.player_stats[player_id]['match_scores'][match_id] = score
                self.player_stats[player_id]['total_score'] += score
    
    def get_score(self, dct):
        """Calculate player score based on the provided formula"""
        batsman_score = 0
        if dct['balls'] > 0:
            sr = dct['runs'] / dct['balls']
            batsman_score = dct['runs'] + (sr - 1.5) * max(dct['runs'], dct['balls']) + (dct['runs'] >= 50) * 8 + (dct['runs'] >= 100) * 8
        
        bowlers_score = 0
        if dct['bowled_balls'] > 0:
            bowlers_score = 3 * (1.5 * dct['bowled_balls'] - dct['conceded']) + dct['wickets'] * 20 + dct['good_one'] * 10 + (dct['wickets'] >= 3) * 15 + dct['dots']
        
        fielding_score = (dct['catches'] + dct['run_outs']) * 10
        
        return batsman_score + bowlers_score + fielding_score + 4
    
    def calculate_additional_stats(self):
        """Calculate additional statistics like averages and strike rates"""
        for player_id, stats in self.player_stats.items():
            batting = stats['batting']
            bowling = stats['bowling']
            
            # Batting averages and strike rates
            if batting['dismissals'] > 0:
                batting['average'] = round(batting['runs'] / batting['dismissals'], 2)
            else:
                batting['average'] = batting['runs'] if batting['runs'] > 0 else 0
            
            if batting['balls_faced'] > 0:
                batting['strike_rate'] = round((batting['runs'] / batting['balls_faced']) * 100, 2)
            else:
                batting['strike_rate'] = 0
            
            # Bowling averages and economy rates
            if bowling['wickets'] > 0:
                bowling['average'] = round(bowling['runs_conceded'] / bowling['wickets'], 2)
            else:
                bowling['average'] = bowling['runs_conceded'] if bowling['runs_conceded'] > 0 else 0
            
            if bowling['balls_bowled'] > 0:
                overs = bowling['balls_bowled'] / 6
                bowling['economy_rate'] = round(bowling['runs_conceded'] / overs, 2) if overs > 0 else 0
            else:
                bowling['economy_rate'] = 0
    
    def save_to_csv(self, output_file="player_stats.csv"):
        """Save player statistics to a CSV file"""
        # Calculate additional statistics
        self.calculate_additional_stats()
        
        # Define CSV columns
        columns = [
            'player_id', 'name', 'team', 'matches_played', 'total_score',
            'batting_runs', 'batting_balls_faced', 'batting_average', 'batting_strike_rate', 
            'batting_fours', 'batting_sixes', 'batting_dismissals',
            'bowling_balls', 'bowling_runs', 'bowling_wickets', 'bowling_average', 'bowling_economy',
            'fielding_catches', 'fielding_run_outs'
        ]
        
        # Write to CSV
        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            writer.writeheader()
            
            for player_id, stats in self.player_stats.items():
                writer.writerow({
                    'player_id': player_id,
                    'name': stats['name'],
                    'team': stats['team'],
                    'matches_played': stats['matches'],
                    'total_score': round(stats.get('total_score', 0), 2),
                    'batting_runs': stats['batting']['runs'],
                    'batting_balls_faced': stats['batting']['balls_faced'],
                    'batting_average': stats['batting'].get('average', 0),
                    'batting_strike_rate': stats['batting'].get('strike_rate', 0),
                    'batting_fours': stats['batting']['fours'],
                    'batting_sixes': stats['batting']['sixes'],
                    'batting_dismissals': stats['batting']['dismissals'],
                    'bowling_balls': stats['bowling']['balls_bowled'],
                    'bowling_runs': stats['bowling']['runs_conceded'],
                    'bowling_wickets': stats['bowling']['wickets'],
                    'bowling_average': stats['bowling'].get('average', 0),
                    'bowling_economy': stats['bowling'].get('economy_rate', 0),
                    'fielding_catches': stats.get('fielding', {}).get('catches', 0),
                    'fielding_run_outs': stats.get('fielding', {}).get('run_outs', 0)
                })
        
        print(f"Player statistics saved to {output_file}")
    
    def save_to_json(self, output_file="player_stats.json"):
        """Save player statistics to a JSON file"""
        # Calculate additional statistics
        self.calculate_additional_stats()
        
        # Prepare data for serialization
        output_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "player_count": len(self.player_stats),
                "matches_processed": len(self.processed_matches)
            },
            "players": {}
        }
        
        for player_id, stats in self.player_stats.items():
            # Format match scores as array for better readability
            match_scores = []
            for match_id, score in stats.get('match_scores', {}).items():
                match_scores.append({
                    "match_id": match_id,
                    "score": round(score, 2)
                })
            
            output_data["players"][player_id] = {
                "player_name": stats['name'],
                "team": stats['team'],
                "matches": stats['matches'],
                "total_score": round(stats.get('total_score', 0), 2),
                "match_scores": match_scores,
                "batting": stats['batting'],
                "bowling": stats['bowling'],
                "fielding": stats.get('fielding', {"catches": 0, "run_outs": 0})
            }
        
        # Write to JSON file
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"Player statistics saved to {output_file}") 