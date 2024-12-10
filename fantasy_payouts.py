import json
from collections import defaultdict

# Load JSON files
def load_json(filename):
    with open(filename, 'r') as file:
        return json.load(file)

# Save JSON files
def save_json(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

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
    # Load data
    weekly_data = load_json("weeklydata.json")
    season_data = load_json("seasondata.json")

    # Calculate payouts
    payouts = calculate_payouts(weekly_data, season_data)

    # Save to payouts.json
    save_json("payouts.json", payouts)
    print("payouts.json generated successfully.")

if __name__ == "__main__":
    main()
