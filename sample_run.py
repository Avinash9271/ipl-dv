#!/usr/bin/env python3
"""
Sample script to demonstrate the Cricket Player Statistics Analyzer with mock data.
This can be used to test the functionality without making actual API calls.
"""

import json
from stats_processor import StatsProcessor

# Sample ball-by-ball data based on the provided example
SAMPLE_MATCH_DATA = {
    "data": {
        "id": "23ded5c0-112b-411e-a23c-b209bf5cc4ff",
        "name": "New Zealand vs Pakistan, 4th T20I",
        "bbb": [
            {
                "n": 1,
                "inning": 0,
                "over": 0,
                "ball": 1,
                "batsman": {
                    "id": "812fc568-a932-4f29-a1c4-b7c929e6a248",
                    "name": "Tim Seifert"
                },
                "bowler": {
                    "id": "df7bffbc-02e6-41ef-8049-fd256c850fe8",
                    "name": "Shaheen Afridi"
                },
                "runs": 0,
                "extras": 0
            },
            {
                "n": 2,
                "inning": 0,
                "over": 0,
                "ball": 2,
                "batsman": {
                    "id": "812fc568-a932-4f29-a1c4-b7c929e6a248",
                    "name": "Tim Seifert"
                },
                "bowler": {
                    "id": "df7bffbc-02e6-41ef-8049-fd256c850fe8",
                    "name": "Shaheen Afridi"
                },
                "runs": 4,
                "extras": 0
            },
            {
                "n": 3,
                "inning": 0,
                "over": 0,
                "ball": 3,
                "batsman": {
                    "id": "812fc568-a932-4f29-a1c4-b7c929e6a248",
                    "name": "Tim Seifert"
                },
                "bowler": {
                    "id": "df7bffbc-02e6-41ef-8049-fd256c850fe8",
                    "name": "Shaheen Afridi"
                },
                "runs": 0,
                "extras": 0
            },
            {
                "n": 4,
                "inning": 0,
                "over": 0,
                "ball": 4,
                "batsman": {
                    "id": "812fc568-a932-4f29-a1c4-b7c929e6a248",
                    "name": "Tim Seifert"
                },
                "bowler": {
                    "id": "df7bffbc-02e6-41ef-8049-fd256c850fe8",
                    "name": "Shaheen Afridi"
                },
                "runs": 0,
                "extras": 0
            },
            {
                "n": 5,
                "inning": 0,
                "over": 0,
                "ball": 5,
                "batsman": {
                    "id": "812fc568-a932-4f29-a1c4-b7c929e6a248",
                    "name": "Tim Seifert"
                },
                "bowler": {
                    "id": "df7bffbc-02e6-41ef-8049-fd256c850fe8",
                    "name": "Shaheen Afridi"
                },
                "runs": 0,
                "extras": 0
            },
            {
                "n": 6,
                "inning": 0,
                "over": 0,
                "ball": 6,
                "batsman": {
                    "id": "812fc568-a932-4f29-a1c4-b7c929e6a248",
                    "name": "Tim Seifert"
                },
                "bowler": {
                    "id": "df7bffbc-02e6-41ef-8049-fd256c850fe8",
                    "name": "Shaheen Afridi"
                },
                "runs": 1,
                "extras": 0
            },
            # Add a wicket (caught)
            {
                "n": 7,
                "inning": 0,
                "over": 1,
                "ball": 1,
                "batsman": {
                    "id": "943e3a5a-5d1f-4c0e-978d-2a0a3b2a53e0",
                    "name": "Devon Conway"
                },
                "bowler": {
                    "id": "df7bffbc-02e6-41ef-8049-fd256c850fe8",
                    "name": "Shaheen Afridi"
                },
                "runs": 0,
                "extras": 0,
                "wicket": {
                    "type": "caught",
                    "player": {
                        "id": "943e3a5a-5d1f-4c0e-978d-2a0a3b2a53e0",
                        "name": "Devon Conway"
                    },
                    "bowler": {
                        "id": "df7bffbc-02e6-41ef-8049-fd256c850fe8",
                        "name": "Shaheen Afridi"
                    },
                    "fielder": {
                        "id": "ab123456-7890-abcd-efgh-123456789012",
                        "name": "Babar Azam"
                    }
                }
            },
            # Add a wicket (bowled)
            {
                "n": 8,
                "inning": 0,
                "over": 1,
                "ball": 2,
                "batsman": {
                    "id": "123e4567-e89b-12d3-a456-426614174001",
                    "name": "Kane Williamson"
                },
                "bowler": {
                    "id": "df7bffbc-02e6-41ef-8049-fd256c850fe8",
                    "name": "Shaheen Afridi"
                },
                "runs": 0,
                "extras": 0,
                "wicket": {
                    "type": "bowled",
                    "player": {
                        "id": "123e4567-e89b-12d3-a456-426614174001",
                        "name": "Kane Williamson"
                    },
                    "bowler": {
                        "id": "df7bffbc-02e6-41ef-8049-fd256c850fe8",
                        "name": "Shaheen Afridi"
                    }
                }
            },
            # Add a run out
            {
                "n": 9,
                "inning": 0,
                "over": 1,
                "ball": 3,
                "batsman": {
                    "id": "234e5678-e89b-12d3-a456-426614174002",
                    "name": "Glenn Phillips"
                },
                "bowler": {
                    "id": "df7bffbc-02e6-41ef-8049-fd256c850fe8",
                    "name": "Shaheen Afridi"
                },
                "runs": 0,
                "extras": 0,
                "wicket": {
                    "type": "run out",
                    "player": {
                        "id": "234e5678-e89b-12d3-a456-426614174002",
                        "name": "Glenn Phillips"
                    },
                    "fielder": {
                        "id": "cd123456-7890-abcd-efgh-123456789013",
                        "name": "Shadab Khan"
                    }
                }
            }
        ]
    }
}

def main():
    print("Cricket Player Statistics Analyzer - Sample Run")
    print("==============================================")
    
    # Create stats processor
    processor = StatsProcessor()
    
    # Process sample match data
    print("\nProcessing sample match data...")
    processor.process_match(SAMPLE_MATCH_DATA)
    
    # Get the stats dataframe
    stats_df = processor.get_stats_dataframe()
    
    # Display the stats
    print("\nPlayer Statistics:")
    print("=================")
    print(stats_df.to_string(index=False))
    
    # Save to CSV
    output_file = "sample_player_stats.csv"
    stats_df.to_csv(output_file, index=False)
    print(f"\nSample statistics saved to {output_file}")
    
    # Save the sample data as JSON for reference
    with open("sample_match_data.json", "w") as f:
        json.dump(SAMPLE_MATCH_DATA, f, indent=2)
    
    print("\nSample run complete!")

if __name__ == "__main__":
    main() 