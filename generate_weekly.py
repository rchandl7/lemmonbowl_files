import json

def generate_weekly_data(api_data):
    weekly_data = []

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
                "Top Payout": "$50",
                "Bottom TeamName": bottom_team_name,
                "Bottom WeeklyPoints": f"{bottom_team.get('totalPoints', 0):.2f}",
                "Bottom Payout": "-$10"
            })

    return weekly_data

def update_season_data(api_data, season_data):
    # Update Reg Season Champ
    reg_season_champ = next((team for team in api_data["teams"] if team.get("playoffSeed") == 1), None)
    reg_season_champ_name = reg_season_champ.get("name", "tba") if reg_season_champ else "tba"
    season_data[0]["TeamName"] = reg_season_champ_name

    # Update Playoff Champ
    playoff_champ = next((team for team in api_data["teams"] if team.get("rankFinal") == 1), None)
    playoff_champ_name = playoff_champ.get("name", "tba") if playoff_champ else "tba"
    season_data[2]["TeamName"] = playoff_champ_name

    # Update Playoff Runner Up
    playoff_runner_up = next((team for team in api_data["teams"] if team.get("rankFinal") == 2), None)
    playoff_runner_up_name = playoff_runner_up.get("name", "tba") if playoff_runner_up else "tba"
    season_data[1]["TeamName"] = playoff_runner_up_name

    return season_data

def main():
    # Load the API data from the local file
    with open('api_data.json', 'r') as api_data_file:
        api_data = json.load(api_data_file)

    # Generate weekly data
    weekly_data = generate_weekly_data(api_data)

    # Write the weekly data to weeklydata.json
    with open('weeklydata.json', 'w') as weekly_file:
        json.dump(weekly_data, weekly_file, indent=4)

    # Load the season data from the local file
    with open('seasondata.json', 'r') as season_data_file:
        season_data = json.load(season_data_file)

    # Update season data with team names
    updated_season_data = update_season_data(api_data, season_data)

    # Write the updated season data to seasondata.json
    with open('seasondata.json', 'w') as season_file:
        json.dump(updated_season_data, season_file, indent=4)

if __name__ == "__main__":
    main()
