import requests
import json_extractor
import upload
import time
from bs4 import BeautifulSoup
from import_gis import import_gis
from data_sources import minWait

lastDatapointsUpdate = 0
name = "Russia"

def import_data():
    global lastDatapointsUpdate

    url = "https://xn--80aesfpebagmfblc0a.xn--p1ai/"
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    stats = soup.select(".cv-countdown__item-value span")
    
    total = stats[1]
    recovered = stats[3]
    deaths = stats[4]
    datapoint = {
        "country": "Russia",
        "total": int(total.text.replace(" ", "")),
        "recovered": int(recovered.text.replace(" ", "")),
        "deaths": int(deaths.text.replace(" ", ""))
    }
    
    if upload.upload_datapoints([datapoint]):
        lastDatapointsUpdate = time.time()

if __name__ == "__main__":
    import_data()