import requests
from bs4 import BeautifulSoup
from data_sources import source

@source('live', name='Bermuda')
def import_data():
    url = 'https://www.gov.bm/coronavirus-covid19-update'
    soup = BeautifulSoup(requests.get(url, timeout=10).text, 'html.parser')
    statsTable = soup.select(  "table"  )[1]
    statsRows = statsTable.select("tr")
    tests = int(statsRows[1].select("td")[-1].text)
    total = int(statsRows[3].select("td")[-1].text)
    recovered = int(statsRows[10].select("td")[-1].text)
    deaths = int(statsRows[13].select("td")[-1].text)
    
    yield {
        "country": "Bermuda",
        "tests": tests,
        "total": total,
        "recovered": recovered,
        "deaths": deaths
    }

if __name__ == "__main__":
    import_data()