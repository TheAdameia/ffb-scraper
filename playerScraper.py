import requests
from bs4 import BeautifulSoup
import pandas as pd

# source venv/Scripts/activate
# deactivate

teams = [
    "ARI", "ATL", "BAL", "BUF", "CAR", "CHI", "CIN", "CLE", "DAL", "DEN",
    "DET", "GB", "HOU", "IND", "JAX", "KC", "LV", "LAC", "LAR", "MIA",
    "MIN", "NE", "NO", "NYG", "NYJ", "PHI", "PIT", "SEA", "SF", "TB",
    "TEN", "WAS"
]

# I will need to add in some conditions for DST since that's formatted differently
positions = [
    "qb", "rb", "wr", "te", "k", "dst"
]

base_url = "https://fantasydata.com/nfl/fantasy-football-leaders"
params_template = {
    "scope": "season",
    "sp": "2020_REG",  # season/year
    "position": "",    # placeholder for position
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
    for position in positions:
        params = params_template.copy()
        params["team"] = team
        params["position"] = [position]

        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table")
        if not table:
            print(f"Warning: No table found for team {team}")
            continue

        for row in table.find_all("tr")[1:]:  # Skip header
            cells = row.find_all("td")

            name_cell = row.find("td", class_="sticky special text-start")
            player_link = name_cell.find("a") if name_cell else None
            player_id = None

            if player_link and "href" in player_link.attrs:
                href = player_link["href"]
                # Extract the numeric ID from the URL
                # URL format: /nfl/kyler-murray-fantasy/20889
                player_id = href

            data = [cell.get_text(strip=True) for cell in cells[:5]] # five total columns

            # consider case switch for 8, 10, whatever games played by position
            if data and position == "dst":
                data.append(player_id)
                all_rows.append(data)
            elif data and len(data) == 5:
                try:
                    #check games played
                    if float(data[4]) >= 10: # GP is 5th column (index 4)
                        if position == "rb" and data[3] == "FB":
                            continue # skips fullbacks
                        data.append(player_id)
                        all_rows.append(data)
                except ValueError:
                    pass #skips non-integer data in that column

# Convert to DataFrame
columns = ["Rank", "Name", "Team", "Pos", "GP", "PlayerID"]
df = pd.DataFrame(all_rows, columns=columns)

print(df.head())

year = params_template["sp"]  # for the file save

df.to_csv(f"all_team_stats_{year}.csv", index=False)
