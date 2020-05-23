import requests
from bs4 import BeautifulSoup
from data_sources import source

@source('live', name='Paraguay')
def import_data():
    url = "https://www.mspbs.gov.py/covid-19.php"
    soup = BeautifulSoup(requests.get(url, verify=False, timeout=10).text, "html.parser")
    stats = soup.select("font > font")

    yield {
        "country": "Paraguay",
        "total": int(stats[0].text.strip()),
        "deaths": int(stats[1].text.strip()),
        "recovered": int(stats[2].text.strip())
    }