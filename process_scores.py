import json
import pandas as pd

# Load the JSON data
file_path = "2024/api_data.json"  # Replace with the actual file path
with open(file_path, "r") as f:
    data = json.load(f)

# Extract schedule
schedule = data["schedule"]

# Initialize team data
teams = {}
for team in data["teams"]:
    teams[team["id"]] = {
        "name": team["name"],
        "matchup_wins": 0,         # calculated H2H wins
        "matchup_losses": 0,       # calculated H2H losses
        "points_for": 0,
        "points_against": 0,
        "actual_wins": team["record"]["overall"]["wins"],
        "actual_losses": team["record"]["overall"]["losses"],
        "actual_rank": team.get("rank") or team.get("playoffSeed") or None
    }

# Process matchups
for match in schedule:
    # Only process matchups in period 1 through 14
    if not (1 <= match.get("matchupPeriodId", 0) <= 14):
        continue
    if "home" not in match or "away" not in match:
        continue
    if "totalPoints" not in match["home"] or "totalPoints" not in match["away"]:
        continue

    home_id = match["home"]["teamId"]
    away_id = match["away"]["teamId"]
    home_pts = match["home"]["totalPoints"]
    away_pts = match["away"]["totalPoints"]

    # Track points for/against
    teams[home_id]["points_for"] += home_pts
    teams[home_id]["points_against"] += away_pts
    teams[away_id]["points_for"] += away_pts
    teams[away_id]["points_against"] += home_pts

    # Head-to-head win/loss
    if home_pts > away_pts:
        teams[home_id]["matchup_wins"] += 1
        teams[away_id]["matchup_losses"] += 1
    elif away_pts > home_pts:
        teams[away_id]["matchup_wins"] += 1
        teams[home_id]["matchup_losses"] += 1
    # ties → no result

# Convert results to DataFrame
results = pd.DataFrame.from_dict(teams, orient="index")

# Order columns for output
results = results[
    [
        "name",
        "matchup_wins",
        "matchup_losses",
        "points_for",
        "points_against",
        "actual_rank",
        "actual_wins",
        "actual_losses"
    ]
].sort_values(by=["matchup_wins", "matchup_losses"], ascending=[False, True])

# Save CSV
output_file = "final_team_records.csv"
results.to_csv(output_file, index=False)

print(f"Results have been saved to {output_file}")
