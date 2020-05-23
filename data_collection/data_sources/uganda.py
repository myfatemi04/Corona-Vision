import requests
from bs4 import BeautifulSoup
from data_sources import source

@source('live', name='Uganda')
def import_data():
    url = "https://covid19.gou.go.ug/"
    soup = BeautifulSoup(requests.get(url, verify=False, timeout=10).text, 'html.parser')
    stats = soup.select(  "div.number font"  )

    yield {
        "country": "Uganda",
        "tests": int(stats[0].text.replace(",", "")),
        "total": int(stats[1].text.replace(",", "")),
        "recovered": int(stats[2].text.replace(",", "")),
    }

    active = int(stats[3].text.replace(",", ""))

    datapoint['deaths'] = datapoint['total'] - active - datapoint['recovered']
    
    

if __name__ == "__main__":
    import_data()