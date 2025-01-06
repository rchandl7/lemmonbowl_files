import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env for local development
load_dotenv()

# Get API details from environment variables or fallback to defaults
SWID = os.getenv("SWID")
espn_s2 = os.getenv("ESPN_S2")
league_id = os.getenv("LEAGUE_ID")

# Check if the necessary environment variables are available
if not SWID or not espn_s2 or not league_id:
    raise ValueError("Missing required API credentials. Ensure they are set in GitHub Secrets or a local .env file.")

# Load season data
with open("seasons.json", "r") as seasons_file:
    seasons_data = json.load(seasons_file)

# Find the current season ID
current_season_id = next((season["id"] for season in seasons_data["seasons"] if season.get("current")), None)
if not current_season_id:
    raise ValueError("No current season found in seasons.json. Please ensure one season has 'current': true.")

# Base API URL
BASE_URL = f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{current_season_id}/segments/0/leagues/{league_id}"

def fetch_weekly_data():
    url = f"{BASE_URL}?view=modular&view=mNav&view=mMatchupScore&view=mScoreboard&view=mSettings&view=mTopPerformers&view=mTeam"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        response = requests.get(url, cookies={"SWID": SWID, "espn_s2": espn_s2}, headers=headers)
        print(f"Status Code: {response.status_code}")

        if response.headers.get("Content-Type", "").startswith("text/html"):
            print("HTML response detected. Likely an error page:")
            print(response.text)
            return None

        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def main():
    print("Fetching weekly data...")
    weekly_data = fetch_weekly_data()
    if weekly_data is None:
        print("Failed to fetch weekly data.")
        return

    os.makedirs(current_season_id, exist_ok=True)
    with open(f"{current_season_id}/api_data.json", "w") as outfile:
        json.dump(weekly_data, outfile, indent=4)
    print(f"Data written to {current_season_id}/api_data.json.")

if __name__ == "__main__":
    main()
