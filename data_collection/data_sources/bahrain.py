import requests
from bs4 import BeautifulSoup
from data_sources import source

@source('live', name='Bahrain')
def import_data():
    url = "https://www.moh.gov.bh/?lang=en"
    soup = BeautifulSoup(requests.get(url, timeout=10).text, 'html.parser')
    stats = soup.select("table thead span")
    tests = stats[0].text
    active = stats[1].text
    serious = stats[3].text
    recovered = stats[4].text
    deaths = stats[5].text
    yield {
        "country": "Bahrain",
        "tests": int(tests),
        "total": int(active) + int(recovered) + int(deaths),
        "recovered": int(recovered),
        "deaths": int(deaths),
        "serious": int(serious)
    }

if __name__ == "__main__":
    import_data()