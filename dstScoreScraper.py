import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import sys

# python dstScoreScraper.py <year>


if len(sys.argv) != 2:
    print("Usage: python dstScoreScraper.py <year>")
    sys.exit(1)

year = sys.argv[1]

headers = {
    "User-Agent": "Mozilla/5.0"
}

teams = [
    "ARI", "ATL", "BAL", "BUF", "CAR", "CHI", "CIN", "CLE", "DAL", "DEN",
    "DET", "GB", "HOU", "IND", "JAX", "KC", "LV", "LAC", "LAR", "MIA",
    "MIN", "NE", "NO", "NYG", "NYJ", "PHI", "PIT", "SEA", "SF", "TB",
    "TEN", "WAS"
]

DST_index = {
    "Week": 2,
    "PointsAgainst": 12,
    "Sacks": 5,
    "InterceptionDefense": 7,
    "DefenseFumbleRecovery": 8,
    "Safety": 9,
    "TouchdownsDefense": 10,
    "TouchdownsReturn": 11,
    "FantasyPoints": 13
}

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

def map_row_to_standard(data, position_map):
    row_dict = {header: None for header in standard_headers}
    for key, index in position_map.items():
        if index < len(data):
            row_dict[key] = data[index]
    return row_dict


base_url = "https://fantasydata.com/nfl/fantasy-football-leaders"
all_rows = []

# Helper. Fetches, parses data.
def fetch_team_data(team, week_from, week_to):
    params = {
        "scope": "game",
        "sp": f"{year}_REG",
        "week_from": str(week_from),
        "week_to": str(week_to),
        "position": "dst",
        "team": team,
        "scoring": "fpts_yahoo",
        "order_by": "gp",
        "sort_dir": "desc"
    }

    response = requests.get(base_url, headers=headers, params=params)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table")

    if not table:
        print(f"No table found for {team} Weeks {week_from}-{week_to}")
        return []

    rows = []

    for tr in table.find_all("tr")[1:]:
        tds = tr.find_all("td")
        if not tds:
            continue
        row = [td.text.strip() for td in tds]
        rows.append(row)

    return rows


for team in teams:
    print(f"Fetching data for {team}...")

    for start_week, end_week in [(1, 10), (11, 18)]:
        rows = fetch_team_data(team, start_week, end_week)

        for row in rows:
            standard_row = map_row_to_standard(row, DST_index)
            standard_row["Position"] = "DST"
            standard_row["PlayerID"] = None  # DST has no playerId
            standard_row["Team"] = team
            all_rows.append(standard_row)

        time.sleep(1)  # courtesy


if all_rows:
    df = pd.DataFrame(all_rows, columns=standard_headers)
    df.to_csv(f"dst_score_{year}.csv", index=False)
    print(f"Saved data to dst_score_{year}.csv")
else:
    print("No data found.")