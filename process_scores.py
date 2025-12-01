import json
import pandas as pd

# Load the JSON data
file_path = "2025/api_data.json"  # Replace with the actual file path
with open(file_path, "r") as f:
    data = json.load(f)

# Extract the schedule and team information
schedule = data["schedule"]

# Initialize team win/loss counters
teams = {
    team["id"]: {
        "name": team["name"],
        "wins": 0,
        "losses": 0
    }
    for team in data["teams"]
}

# Process each matchup and assign wins/losses
for match in schedule:
    # Skip invalid matchups
    if "home" not in match or "away" not in match:
        continue
    if "totalPoints" not in match["home"] or "totalPoints" not in match["away"]:
        continue

    home_id = match["home"]["teamId"]
    away_id = match["away"]["teamId"]
    home_pts = match["home"]["totalPoints"]
    away_pts = match["away"]["totalPoints"]

    # Head-to-head win/loss
    if home_pts > away_pts:
        teams[home_id]["wins"] += 1
        teams[away_id]["losses"] += 1
    elif away_pts > home_pts:
        teams[away_id]["wins"] += 1
        teams[home_id]["losses"] += 1
    # If exact tie → no wins/losses

# Convert results into a DataFrame
results = pd.DataFrame.from_dict(teams, orient="index")
results = results[["name", "wins", "losses"]].sort_values(
    by=["wins", "losses"], ascending=[False, True]
)

# Save results to CSV
output_file = "final_team_records.csv"
results.to_csv(output_file, index=False)

print(f"Results have been saved to {output_file}")
