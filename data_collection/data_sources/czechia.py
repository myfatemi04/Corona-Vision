import requests
from bs4 import BeautifulSoup
from data_sources import source

@source('live', name='Czechia')
def import_data():
    url = "https://onemocneni-aktualne.mzcr.cz/covid-19"
    soup = BeautifulSoup(requests.get(url, timeout=10).text, "html.parser")
    yield {
        'country': 'Czechia',
        'tests': int(soup.select_one("#count-test").text.replace(" ", "")),
        'total': int(soup.select_one("#count-sick").text.replace(" ", "")),
        'recovered': int(soup.select_one("#count-recover").text.replace(" ", "")),
        'deaths': int(soup.select_one("#count-dead").text.replace(" ", "")),
    }

if __name__ == "__main__":
    import_data()