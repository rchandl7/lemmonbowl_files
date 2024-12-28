import requests
import json
import os

with open("seasons.json", "r") as seasons_file:
    seasons_data = json.load(seasons_file)

# Find the current season ID
current_season_id = None
for season in seasons_data["seasons"]:
    if season.get("current"):  # Use .get() to avoid KeyError
        current_season_id = season["id"]
        print (current_season_id)
        break

# Handle the case where no current season is found
if not current_season_id:
    raise ValueError("No current season found in seasons.json. Please ensure one season has 'current': true.")

# API Details
SWID = "{1043CB14-2868-48AE-9C4D-D27D4CCE624D}"
espn_s2 = "AEAqbX3DWl%2F9%2BNUv77s%2Fk6gOOpqRvIvgAwbCHtYeB2C%2FTtCK0Af4k6iozwQAyP3XyY0NJ2ck6JBQFXvgE7Lpr4m%2Fa47A1FivDpWxfjMNztezL5cis1t6UoKtgH%2BCgSckkm5R%2Fe6ObR3rfMEof2vLSXy3hbeZnNtq5OenItleEU8rpBNk3UZHjfXLQZvBlYKyKGuIqQ0qwQgyYoIExLR9UfdSVhnJlbdA%2B6SlKgq4RPvG97bVOH0NGbp4xxjYeNc1%2F4eL5HLpqA%2B1aeamNeym%2FG9ewvdWIJoRCPwlof5pPbY%2FaQ%3D%3D"
league_id = "160513"
season_id = current_season_id
BASE_URL = f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{season_id}/segments/0/leagues/{league_id}"

def fetch_weekly_data():
    # URL with all necessary views
    url = f"{BASE_URL}?view=modular&view=mNav&view=mMatchupScore&view=mScoreboard&view=mSettings&view=mTopPerformers&view=mTeam"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, cookies={"SWID": SWID, "espn_s2": espn_s2}, headers=headers)
        print(f"Status Code: {response.status_code}")

        # Debugging: Print raw HTML if returned
        if response.headers.get("Content-Type", "").startswith("text/html"):
            print("HTML response detected. Likely an error page:")
            print(response.text)
            return None

        # Parse JSON response
        try:
            data = response.json()
            return data
        except requests.exceptions.JSONDecodeError:
            print("Error: Unable to parse JSON. Response content:")
            print(response.text)
            return None

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def main():
    print("Fetching weekly data...")
    weekly_data = fetch_weekly_data()
    if weekly_data is None:
        print("Failed to fetch weekly data.")
        return

    print("Weekly data fetched successfully!")
    # Save the data to a JSON file for further processing
    os.makedirs(season_id, exist_ok=True)

    with open(f"{season_id}/api_data.json", "w") as outfile:
        json.dump(weekly_data, outfile, indent=4)
    print("Data written to ", season_id,"/api_data.json.")

if __name__ == "__main__":
    main()
