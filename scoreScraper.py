import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import argparse
import os

# to run this, run
# python scoreScraper.py all_team_stats_{whenever}.csv


# just going to have to write index maps per position.

QB_index = {
    "Completions": 5,
    "AttemptsPassing": 6,
    "YardsPassing": 8,
    "TouchdownsPassing": 10,
    "Interceptions": 11,
    "AttemptsRushing": 15,
    "YardsRushing": 16,
    "TouchdownsRushing": 18,
    "Week": 0,
    "FantasyPoints": 4,
    "Team": 2
}

WR_index = {
    "Receptions": 5,
    "Targets": 6,
    "YardsReceiving": 7,
    "TouchdownsReceiving": 8,
    "AttemptsRushing": 12,
    "YardsRushing": 13,
    "TouchdownsRushing": 15,
    "Fumbles": 16,
    "FumblesLost": 17,
    "Week": 0,
    "FantasyPoints": 4,
    "Team": 2
}

RB_index = {
    "Receptions": 9,
    "Targets": 10,
    "YardsReceiving": 11,
    "TouchdownsReceiving": 12,
    "AttemptsRushing": 5,
    "YardsRushing": 6,
    "TouchdownsRushing": 8,
    "Fumbles": 13,
    "FumblesLost": 14,
    "Week": 0,
    "FantasyPoints": 4,
    "Team": 2
}

TE_index ={
    "Receptions": 5,
    "Targets": 6,
    "YardsReceiving": 7,
    "TouchdownsReceiving": 8,
    "AttemptsRushing": 12,
    "YardsRushing": 13,
    "TouchdownsRushing": 15,
    "Fumbles": 16,
    "FumblesLost": 17,
    "Week": 0,
    "FantasyPoints": 4,
    "Team": 2
}

K_index = {
    "FieldGoalAttempts": 6,
    "FieldGoalsMade": 5,
    "ExtraPointAttempt": 10,
    "ExtraPointMade": 9,
    "Week": 0,
    "FantasyPoints": 4,
    "Team": 2
}

# and standard headers for the actual recording.

standard_headers = [
    "Completions",
    "AttemptsPassing",
    "YardsPassing",
    "TouchdownsPassing",
    "Interceptions",
    "Targets",
    "Receptions",
    "YardsReceiving",
    "TouchdownsReceiving",
    "AttemptsRushing",
    "YardsRushing",
    "TouchdownsRushing",
    "Fumbles",
    "FumblesLost",
    "TwoExtraPoints",
    "FieldGoalAttempts",
    "FieldGoalsMade",
    "ExtraPointAttempts",
    "ExtraPointMade",
    "PointsAgainst",
    "Sacks",
    "InterceptionDefense",
    "DefenseFumbleRecovery",
    "Safety",
    "TouchdownsDefense",
    "TouchdownsReturn",
    "BlockedKicks",
    "FantasyPoints",
    "Week",
    "PlayerID",
    "Position",
    "Team"
]


parser = argparse.ArgumentParser(description="Scrape FantasyData player stats from input CSV")
parser.add_argument("csv_file", help="CSV file containing player data")
args = parser.parse_args()

input_filename = args.csv_file
if not os.path.exists(input_filename):
    print(f"Error: File '{input_filename}' does not exist.")
    exit(1)

season_segment = os.path.splitext(os.path.basename(input_filename))[0].replace("all_team_stats_", "")

players = pd.read_csv(input_filename)

headers = {
    "User-Agent": "Mozilla/5.0"
}

all_rows = []


# for loop begins here
for _, row in players.iterrows():
    name = row["Name"]
    position = row["Pos"]
    player_id_path = row["PlayerID"]

    if not isinstance(player_id_path, str) or not player_id_path.startswith("/nfl/"):
        print(f"skipping invalid player path for {name}: '{player_id_path}'")
        continue

    base_url = f"https://fantasydata.com{player_id_path}?scoring=fpts_yahoo&sp={season_segment}"

    print(f"scraping scores for player {player_id_path}")

    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to retrieve {name}: {e}")
        continue

    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.find_all("table")
    target_table = tables[2]  # zero-based index

    if not target_table:
        print(f"Warning: No third table found")

    def map_row_to_standard(data, position_map):
        row_dict = {header: None for header in standard_headers}
        for key, index in position_map.items():
            if index < len(data):
                row_dict[key] = data[index]
        return row_dict


    for row in target_table.find_all("tr")[2:]:  # skip header and strangely empty first row
        cells = row.find_all("td")
        data = [cell.get_text(strip=True) for cell in cells]

        if not data:
            continue
        match position:
            case "QB":
                position_map = QB_index
            case "RB":
                position_map = RB_index
            case "WR":
                position_map = WR_index
            case "TE":
                position_map = TE_index
            case "K":
                position_map = K_index
            case _:
                print(f"Unknown position: {position}")
                continue

        standard_row = map_row_to_standard(data, position_map)
        standard_row["PlayerID"] = player_id_path
        standard_row["Position"] = position

        all_rows.append(standard_row)
    
    time.sleep(1) # courtesy

# for loop ends here

output_filename = f"all_score_stats_{season_segment}.csv"
df = pd.DataFrame(all_rows, columns=standard_headers)
df.to_csv(output_filename, index=False)
print(f"Scraping complete! Output saved to {output_filename}")