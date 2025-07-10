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
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find("table")

    if not table:
        print(f"No table found for {team} Weeks {week_from}-{week_to}")
        return []

    header_row = [th.text.strip() for th in table.find_all("th")]
    rows = []

    for tr in table.find_all("tr")[1:]:
        tds = tr.find_all("td")
        if not tds:
            continue
        row = [td.text.strip() for td in tds]
        row.insert(0, team)
        rows.append(row)

    return header_row, rows


for team in teams:
    print(f"Fetching data for {team}...")
    team_rows = []
    all_headers = None

    # weeks 1–10
    headers_chunk, rows = fetch_team_data(team, 1, 10)
    team_rows.extend(rows)
    all_headers = headers_chunk if headers_chunk else all_headers
    time.sleep(1)

    # weeks 11–18
    headers_chunk2, rows2 = fetch_team_data(team, 11, 18)
    team_rows.extend(rows2)
    all_headers = headers_chunk2 if headers_chunk2 else all_headers
    time.sleep(1)

    all_rows.extend(team_rows)


if all_rows and all_headers:
    df = pd.DataFrame(all_rows, columns=["Team"] + all_headers)
    df.to_csv(f"dst_score_{year}.csv", index=False)
    print(f"saved data to dst_score_{year}.csv")
else:
    print("no data found.")
