import json
from collections import defaultdict
import os

# Load JSON files
def load_json(filename):
    if not os.path.exists(filename):
        print(f"{filename} does not exist. Returning an empty list.")
        return []  # Default to an empty list if the file doesn't exist
    with open(filename, 'r') as file:
        return json.load(file)

# Save JSON files
def save_json(filename, data):
    os.makedirs(os.path.dirname(filename), exist_ok=True)  # Ensure directory exists
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

# Get current season ID from seasons.json
def get_current_season_id(seasons_filename):
    seasons_data = load_json(seasons_filename)
    for season in seasons_data.get("seasons", []):
        if season.get("current"):  # Check if the 'current' key is True
            return season["id"]
    raise ValueError("No current season found in seasons.json. Please ensure one season has 'current': true.")

# Calculate payouts
def calculate_payouts(weekly_data, season_data):
    team_stats = defaultdict(lambda: {
        "TotalWinnings": 0,
        "TopWeeks": [],
        "BottomWeeks": []
    })

    # Process weekly data
    for week in weekly_data:
        top_team = week["Top TeamName"]
        bottom_team = week["Bottom TeamName"]
        
        # Add top team winnings
        top_payout = float(week["Top Payout"].replace('$', '').replace(',', ''))
        team_stats[top_team]["TotalWinnings"] += top_payout
        team_stats[top_team]["TopWeeks"].append(week["Week"])

        # Deduct bottom team losses
        bottom_payout = float(week["Bottom Payout"].replace('$', '').replace(',', ''))
        team_stats[bottom_team]["TotalWinnings"] += bottom_payout
        team_stats[bottom_team]["BottomWeeks"].append(week["Week"])

    # Process season data
    for season in season_data:
        team_name = season["TeamName"]
        payout = float(season["Payout"].replace('$', '').replace(',', ''))
        team_stats[team_name]["TotalWinnings"] += payout

    # Compile results into a list
    result = [
        {
            "TeamName": team,
            "TotalWinnings": round(stats["TotalWinnings"], 2),
            "TopWeeks": stats["TopWeeks"],
            "BottomWeeks": stats["BottomWeeks"]
        }
        for team, stats in team_stats.items()
    ]

    # Sort by Total Winnings in descending order
    result.sort(key=lambda x: x["TotalWinnings"], reverse=True)
    return result

# Main function
def main():
    # Fetch current season ID
    seasons_filename = "seasons.json"
    current_season_id = get_current_season_id(seasons_filename)
    print(f"Current season ID: {current_season_id}")

    # File paths for current season
    weekly_data_filename = f"{current_season_id}/weekly.json"
    season_data_filename = f"{current_season_id}/season.json"
    payout_filename = f"{current_season_id}/payouts.json"

    # Load or initialize data
    weekly_data = load_json(weekly_data_filename)
    season_data = load_json(season_data_filename)

    if not weekly_data:
        print(f"No weekly data found in {weekly_data_filename}.")
    if not season_data:
        print(f"No season data found in {season_data_filename}.")

    # Calculate payouts
    payouts = calculate_payouts(weekly_data, season_data)

    # Save to payouts.json
    save_json(payout_filename, payouts)
    print(json.dumps(payouts, indent=4))  # Print the result for debugging
    print(f"{payout_filename} generated successfully.")

if __name__ == "__main__":
    main()
