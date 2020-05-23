import requests
from bs4 import BeautifulSoup
from data_sources import source

@source('live', name='Azerbaijan')
def import_data():
    url = "https://koronavirusinfo.az/az/page/statistika/azerbaycanda-cari-veziyyet"
    soup = BeautifulSoup(requests.get(url, timeout=10).text, 'html.parser')
    stats = soup.select(".gray_little_statistic strong")
    yield {
        "country": "Azerbaijan",
        "total": int(stats[0].text.replace(",", "")),
        "recovered": int(stats[1].text.replace(",", "")),
        "deaths": int(stats[4].text.replace(",", "")),
        "tests": int(stats[5].text.replace(",", "")),
    }

if __name__ == "__main__":
    import_data()