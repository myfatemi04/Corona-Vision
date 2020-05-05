import requests
import json_extractor
import upload
import time
from bs4 import BeautifulSoup
from import_gis import import_gis
from data_sources import minWait

lastDatapointsUpdate = 0
name = "Turkey"

def import_data():
    global lastDatapointsUpdate

    url = "https://covid19.saglik.gov.tr/"
    soup = BeautifulSoup(requests.get(url, timeout=10).text, 'html.parser')
    stats = soup.select("li.baslik-k > :nth-child(2)")

    tests = stats[0].text
    total = stats[1].text
    deaths = stats[2].text
    serious = stats[3].text
    recovered = stats[5].text

    datapoint = {
        "country": "Turkey",
        "tests": int(tests.replace(".", "")),
        "total": int(total.replace(".", "")),
        "deaths": int(deaths.replace(".", "")),
        "serious": int(serious.replace(".", "")),
        "recovered": int(recovered.replace(".", ""))
    }
    
    if upload.upload_datapoints([datapoint]):
        lastDatapointsUpdate = time.time()

if __name__ == "__main__":
    import_data()