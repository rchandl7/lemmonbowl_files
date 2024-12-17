import json
import pandas as pd

# Load the JSON data
file_path = "api_data.json"  # Replace with the actual file path
with open(file_path, "r") as f:
    data = json.load(f)

# Extract the schedule and team information
schedule = data["schedule"]
teams = {
    team["id"]: {
        "name": team["name"],  # Use the 'name' field directly
        "wins": team["record"]["overall"]["wins"],
        "losses": team["record"]["overall"]["losses"]
    }
    for team in data["teams"]
}

# Process each week's scores and calculate additional wins/losses
for week in range(1, 15):  # Weeks 1–14
    weekly_scores = []
    for match in schedule:
        if match["matchupPeriodId"] == week:
            # Collect home and away team scores
            if "home" in match and "away" in match:
                if "totalPoints" in match["home"]:
                    weekly_scores.append((match["home"]["teamId"], match["home"]["totalPoints"]))
                if "totalPoints" in match["away"]:
                    weekly_scores.append((match["away"]["teamId"], match["away"]["totalPoints"]))

    # Calculate the median score for the week
    if weekly_scores:
        scores_df = pd.DataFrame(weekly_scores, columns=["teamId", "points"])
        median_score = scores_df["points"].median()

        # Assign wins and losses based on median score
        for team_id, points in weekly_scores:
            if points > median_score:
                teams[team_id]["wins"] += 1
            elif points < median_score:
                teams[team_id]["losses"] += 1

# Convert the results into a DataFrame for output
results = pd.DataFrame.from_dict(teams, orient="index")
results = results[["name", "wins", "losses"]].sort_values(by=["wins", "losses"], ascending=[False, True])

# Save results to a CSV file
output_file = "final_team_records.csv"
results.to_csv(output_file, index=False)

print(f"Results have been saved to {output_file}")
