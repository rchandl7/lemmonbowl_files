import json
import os

def reference_data():
    """Load seasons.json and extract current season data."""
    with open("seasons.json", "r") as seasons_file:
        seasons_data = json.load(seasons_file)

    # Find the current season
    current_season = next((season for season in seasons_data["seasons"] if season.get("current")), None)

    # Handle case where no current season is found
    if not current_season:
        raise ValueError("No current season found in seasons.json. Ensure one season has 'current': true.")

    # Return the current season's details
    return {
        "current_season_id": current_season["id"],
        "weekly_top_payout": current_season.get("weeklyTop", "n/a"),
        "weekly_bottom_payout": current_season.get("weeklyBottom", "n/a"),
        "one_seed_bonus": current_season.get("oneSeed", "n/a"),
        "champ_bonus": current_season.get("champ", "n/a"),
        "runner_up_bonus": current_season.get("runnerUp", "n/a"),
    }


def generate_weekly_data(api_data, season_data):
    weekly_data = []
    weekly_top_payout = season_data["weekly_top_payout"]
    weekly_bottom_payout = season_data["weekly_bottom_payout"]

    # Iterate through each week's matchup data
    for week in api_data["schedule"]:
        week_number = week["matchupPeriodId"]

        # Only process weeks 1 through 14
        if week_number < 1 or week_number > 14:
            continue

        # Collect all matchups for the week
        matchups = []
        if "away" in week and week["away"] is not None:
            matchups.append(week["away"])
        if "home" in week and week["home"] is not None:
            matchups.append(week["home"])

        # Find the top and bottom team by weekly points
        top_team = max(matchups, key=lambda t: t.get("totalPoints", 0), default=None)
        bottom_team = min(matchups, key=lambda t: t.get("totalPoints", 0), default=None)

        if not top_team or not bottom_team:
            continue

        # Get team details from the API data
        def get_team_name(team_id):
            team = next((team for team in api_data["teams"] if team["id"] == team_id), None)
            if team:
                nickname = team.get('name', '').strip()
                return nickname if nickname else "Unknown Team"
            return "Unknown Team"

        top_team_name = get_team_name(top_team["teamId"])
        bottom_team_name = get_team_name(bottom_team["teamId"])

        # Check if the week already exists in weekly_data
        existing_week = next((item for item in weekly_data if item["Week"] == str(week_number)), None)
        
        if existing_week:
            # Update the existing week's top and bottom teams if necessary
            if float(existing_week["Top WeeklyPoints"]) < top_team.get('totalPoints', 0):
                existing_week["Top TeamName"] = top_team_name
                existing_week["Top WeeklyPoints"] = f"{top_team.get('totalPoints', 0):.2f}"
            
            if float(existing_week["Bottom WeeklyPoints"]) > bottom_team.get('totalPoints', 0):
                existing_week["Bottom TeamName"] = bottom_team_name
                existing_week["Bottom WeeklyPoints"] = f"{bottom_team.get('totalPoints', 0):.2f}"
        else:
            # Create a new entry for the week
            weekly_data.append({
                "Week": str(week_number),
                "Top TeamName": top_team_name,
                "Top WeeklyPoints": f"{top_team.get('totalPoints', 0):.2f}",
                "Top Payout": weekly_top_payout,
                "Bottom TeamName": bottom_team_name,
                "Bottom WeeklyPoints": f"{bottom_team.get('totalPoints', 0):.2f}",
                "Bottom Payout": weekly_bottom_payout
            })

    return weekly_data

def update_season_data(api_data, season_data):
    """Generate season payout data with categories, team names, and payouts."""
    # Fetch values from season_data
    one_seed_payout = f"${season_data['one_seed_bonus']}"
    champ_payout = f"${season_data['champ_bonus']}"
    runner_up_payout = f"${season_data['runner_up_bonus']}"

    # Determine team names
    reg_season_champ = next((team for team in api_data["teams"] if team.get("playoffSeed") == 1), None)
    playoff_champ = next((team for team in api_data["teams"] if team.get("rankCalculatedFinal") == 1), None)
    playoff_runner_up = next((team for team in api_data["teams"] if team.get("rankCalculatedFinal") == 2), None)

    reg_season_champ_name = reg_season_champ.get("name", "tba") if reg_season_champ else "tba"
    playoff_champ_name = playoff_champ.get("name", "tba") if playoff_champ else "tba"
    playoff_runner_up_name = playoff_runner_up.get("name", "tba") if playoff_runner_up else "tba"

    return [
        {"Category": "Reg Season Champ", "TeamName": reg_season_champ_name, "Payout": one_seed_payout},
        {"Category": "Playoff Runner Up", "TeamName": playoff_runner_up_name, "Payout": runner_up_payout},
        {"Category": "Playoff Champ", "TeamName": playoff_champ_name, "Payout": champ_payout},
    ]


def main():
    # Extract current season data from seasons.json
    season_data = reference_data()
    current_season_id = season_data["current_season_id"]

    # Construct the API data file name
    api_data_filename = f"{current_season_id}/api_data.json"

    # Load the API data
    try:
        with open(api_data_filename, "r") as api_data_file:
            api_data = json.load(api_data_file)
    except FileNotFoundError:
        print(f"Error: {api_data_filename} not found.")
        return

    # Generate weekly data
    weekly_data = generate_weekly_data(api_data, season_data)

    # Write weekly data to a JSON file
    weekly_data_filename = f"{current_season_id}/weekly.json"
    with open(weekly_data_filename, "w") as weekly_file:
        json.dump(weekly_data, weekly_file, indent=4)
        print(f"Weekly data written to {weekly_data_filename}.")

    # Construct the season data file name
    season_data_filename = f"{current_season_id}/season.json"

    # Generate season-long payout data
    updated_season_data = update_season_data(api_data, season_data)

    # Write updated season payout data to a JSON file
    with open(season_data_filename, "w") as season_file:
        json.dump(updated_season_data, season_file, indent=4)
        print(f"Season payout data written to {season_data_filename}.")

    # Load the season data (if needed as a template or for enrichment)
    try:
        with open(season_data_filename, "r") as season_data_file:
            season_data_content = json.load(season_data_file)
    except FileNotFoundError:
        print(f"Error: {season_data_filename} not found.")
        return


if __name__ == "__main__":
    main()
