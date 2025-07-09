import requests
from bs4 import BeautifulSoup
import pandas as pd

# takes the output of playerScraper
# scrapes score info for particular players
# formats info to csv depending on the position

base_url = "https://fantasydata.com/nfl/kyler-murray-fantasy/20889?scoring=fpts_yahoo&sp=2020_REG"
# params_template = {
# }

headers = {
    "User-Agent": "Mozilla/5.0"
}

all_rows = []

# for loop goes here

response = requests.get(base_url, headers=headers)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")
tables = soup.find_all("table")
target_table = tables[2]  # Zero-based index

if not target_table:
    print(f"Warning: No third table found")

for row in target_table.find_all("tr")[1:]:  # Skip header
        cells = row.find_all("td")
        data = [cell.get_text(strip=True) for cell in cells]
        # add player ID to data
        all_rows.append(data)



# for loop ends here

# columns = ["Rank", "Name", "Team", "Pos", "GP", "PlayerID"]
df = pd.DataFrame(all_rows)

print(df.head())

df.to_csv(f"all_score_stats.csv", index=False)