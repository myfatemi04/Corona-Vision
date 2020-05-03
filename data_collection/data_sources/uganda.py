import requests
import upload
import time
from bs4 import BeautifulSoup
from data_sources import minWait

lastDatapointsUpdate = 0

def import_data():
    global lastDatapointsUpdate

    url = "https://covid19.gou.go.ug/"
    soup = BeautifulSoup(requests.get(url, verify=False).text, 'html.parser')
    stats = soup.select(  "div.number font"  )

    datapoint = {
        "country": "Uganda",
        "tests": int(stats[0].text.replace(",", "")),
        "total": int(stats[1].text.replace(",", "")),
        "recovered": int(stats[2].text.replace(",", "")),
    }

    active = int(stats[3].text.replace(",", ""))

    datapoint['deaths'] = datapoint['total'] - active - datapoint['recovered']
    
    if upload.upload_datapoints([datapoint], url):
        lastDatapointsUpdate = time.time()

if __name__ == "__main__":
    import_data()