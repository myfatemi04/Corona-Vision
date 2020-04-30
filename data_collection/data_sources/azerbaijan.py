import requests
import json_extractor
import upload
import time
from bs4 import BeautifulSoup
from import_gis import import_gis
from data_sources import minWait

lastDatapointsUpdate = 0
name = "Azerbaijan"

def import_data():
    global lastDatapointsUpdate
    
    url = "https://koronavirusinfo.az/az/page/statistika/azerbaycanda-cari-veziyyet"
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    stats = soup.select(".gray_little_statistic strong")
    datapoint = {
        "country": "Azerbaijan",
        "total": int(stats[0].text.replace(",", "")),
        "recovered": int(stats[1].text.replace(",", "")),
        "deaths": int(stats[4].text.replace(",", "")),
        "tests": int(stats[5].text.replace(",", "")),
    }

    if upload.upload_datapoints([datapoint], url):
        lastDatapointsUpdate = time.time()

if __name__ == "__main__":
    import_data()