import requests
from bs4 import BeautifulSoup
import pandas as pd

# source venv/Scripts/activate
# deactivate

url = "https://fantasydata.com/nfl/fantasy-football-leaders?scope=season&sp=2020_REG&position=rb&team=WAS&scoring=fpts_yahoo&order_by=gp&sort_dir=desc"
headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")
table = soup.find("table")

rows = []
for row in table.find_all("tr")[1:]:  # Skip the header row
    cells = row.find_all("td")
    data = [cell.get_text(strip=True) for cell in cells]
    if data:
        rows.append(data)

df = pd.DataFrame(rows)
print(df.head())  # Show the first few rows
