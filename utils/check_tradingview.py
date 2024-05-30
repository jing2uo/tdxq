import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

url = "https://snapcraft.io/tradingview"
response = requests.get(url)
html_content = response.text

soup = BeautifulSoup(html_content, "html.parser")

published_section = soup.find(string="Last updated")
if published_section:
    published_text = published_section.find_next().text.strip()
    published_date_str = published_text.split(" - ")[0].strip()
    published_date = datetime.strptime(published_date_str, "%d %B %Y")
    yesterday = datetime.now() - timedelta(days=1)

    if published_date > yesterday:
        print("有新版")
