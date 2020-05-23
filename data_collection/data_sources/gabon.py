import requests
from bs4 import BeautifulSoup
from data_sources import source

@source('live', name='Gabon')
def import_data():

    url = "https://infocovid.ga"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36"
    }

    soup = BeautifulSoup(requests.get(url, headers=headers, timeout=10).text, 'html.parser')
    stats = soup.select(".vc_col-sm-3 > .vc_column-inner")

    tests = int(stats[0].select("p")[1].text)
    total = int(stats[1].select("p")[1].text)
    deaths = int(stats[2].select("p")[1].text)
    recovered = int(stats[3].select("p")[1].text)

    yield {
        "country": "Gabon",
        "tests": tests,
        "total": total,
        "deaths": deaths,
        "recovered": recovered
    }

if __name__ == "__main__":
    import_data()