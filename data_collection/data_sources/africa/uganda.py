import requests
from bs4 import BeautifulSoup
from data_sources import source
import re

@source('live', name='Uganda')
def import_data():
    url = "https://covid19.gou.go.ug/"
    soup = BeautifulSoup(requests.get(url, verify=False, timeout=10).text, 'html.parser')
    stats = soup.select(  "div.number font"  )

    num = lambda text: int(re.sub("\\D", "", text))

    datapoint = {
        "country": "Uganda",
        "tests": num(stats[0].text),
        "total": num(stats[1].text),
        "recovered": num(stats[2].text),
    }

    active = int(stats[3].text)

    datapoint['deaths'] = datapoint['total'] - active - datapoint['recovered']

    yield datapoint
    

if __name__ == "__main__":
    import_data()