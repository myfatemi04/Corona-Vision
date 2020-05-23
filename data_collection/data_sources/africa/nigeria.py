import requests
from bs4 import BeautifulSoup
from data_sources import source

@source('live', name='Nigeria')
def import_data():
    url = "https://covid19.ncdc.gov.ng/"
    soup = BeautifulSoup(requests.get(url, timeout=10).text, 'html.parser')
    stats = soup.select(".card-body > h2")
    tests = stats[0].text
    total = stats[1].text
    recovered = stats[3].text
    deaths = stats[4].text
    yield {
        "country": "Nigeria",
        "tests": int(tests.replace(",", "")),
        "total": int(total.replace(",", "")),
        "recovered": int(recovered.replace(",", "")),
        "deaths": int(deaths.replace(",", "")),
    }
    
    

if __name__ == "__main__":
    import_data()