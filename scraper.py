import requests
from bs4 import BeautifulSoup
import pandas as pd

teams = [
    "ARI", "ATL", "BAL", "BUF", "CAR", "CHI", "CIN", "CLE", "DAL", "DEN",
    "DET", "GB", "HOU", "IND", "JAX", "KC", "LV", "LAC", "LAR", "MIA",
    "MIN", "NE", "NO", "NYG", "NYJ", "PHI", "PIT", "SEA", "SF", "TB",
    "TEN", "WAS"
]

base_url = "https://fantasydata.com/nfl/fantasy-football-leaders"
params_template = {
    "scope": "season",
    "sp": "2020_REG",  # season/year
    "position": "rb",  # position filter
    "team": "",        # placeholder for team code
    "scoring": "fpts_yahoo",
    "order_by": "gp",
    "sort_dir": "desc"
}

headers = {
    "User-Agent": "Mozilla/5.0"
}

all_rows = []

for team in teams:
    print(f"Scraping team: {team}")
    params = params_template.copy()
    params["team"] = team

    response = requests.get(base_url, headers=headers, params=params)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table")
    if not table:
        print(f"Warning: No table found for team {team}")
        continue

    for row in table.find_all("tr")[1:]:  # Skip header
        cells = row.find_all("td")
        data = [cell.get_text(strip=True) for cell in cells]
        if data:
            all_rows.append(data)

# Convert to DataFrame (optionally name columns)
df = pd.DataFrame(all_rows)

print(df.head())

df.to_csv("all_team_stats.csv", index=False)
