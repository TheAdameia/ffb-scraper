import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import argparse
import os

# to run this, run
# python scoreScraper.py all_team_stats_{whenever}.csv


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

    for row in target_table.find_all("tr")[2:]:  # skip header and strangely empty first row
            cells = row.find_all("td")
            data = [cell.get_text(strip=True) for cell in cells]
            # add player ID to data
            all_rows.append(data)
    
    time.sleep(1) # courtesy

# for loop ends here

output_filename = f"all_score_stats_{season_segment}.csv"
df = pd.DataFrame(all_rows)
df.to_csv(output_filename, index=False)
print(f"Scraping complete! Output saved to {output_filename}")