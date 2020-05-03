import requests
import json_extractor
import upload
import time
from bs4 import BeautifulSoup
from import_gis import import_gis
from data_sources import minWait

lastDatapointsUpdate = 0
name = "Bahrain"

def import_data():
    global lastDatapointsUpdate

    url = "https://www.moh.gov.bh/?lang=en"
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    stats = soup.select("table thead span")
    tests = stats[0].text
    active = stats[1].text
    serious = stats[3].text
    recovered = stats[4].text
    deaths = stats[5].text
    datapoint = {
        "country": "Bahrain",
        "tests": int(tests),
        "total": int(active) + int(recovered) + int(deaths),
        "recovered": int(recovered),
        "deaths": int(deaths),
        "serious": int(serious)
    }
    
    if upload.upload_datapoints([datapoint]):
        lastDatapointsUpdate = time.time()

if __name__ == "__main__":
    import_data()