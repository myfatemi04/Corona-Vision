import requests
import json_extractor
from bs4 import BeautifulSoup
from data_sources import source

@source('live', name='Russia')
def import_data():
    
    url = "https://xn--80aesfpebagmfblc0a.xn--p1ai/"
    soup = BeautifulSoup(requests.get(url, timeout=10).text, 'html.parser')
    stats = soup.select(".cv-countdown__item-value span")
    
    total = stats[1]
    recovered = stats[3]
    deaths = stats[4]
    yield {
        "country": "Russia",
        "total": int(total.text.replace(" ", "")),
        "recovered": int(recovered.text.replace(" ", "")),
        "deaths": int(deaths.text.replace(" ", ""))
    }
    
    

if __name__ == "__main__":
    import_data()