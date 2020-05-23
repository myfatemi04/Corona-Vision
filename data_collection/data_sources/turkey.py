import requests
from bs4 import BeautifulSoup
from data_sources import source

@source('live', name='Turkey')
def import_data():
    
    url = "https://covid19.saglik.gov.tr/"
    soup = BeautifulSoup(requests.get(url, timeout=10).text, 'html.parser')
    stats = soup.select("li.baslik-k > :nth-child(2)")

    tests = stats[0].text
    total = stats[1].text
    deaths = stats[2].text
    serious = stats[3].text
    recovered = stats[5].text

    yield {
        "country": "Turkey",
        "tests": int(tests.replace(".", "")),
        "total": int(total.replace(".", "")),
        "deaths": int(deaths.replace(".", "")),
        "serious": int(serious.replace(".", "")),
        "recovered": int(recovered.replace(".", ""))
    }
    
    

if __name__ == "__main__":
    import_data()