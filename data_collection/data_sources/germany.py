import requests
import json_extractor
import upload
import time
from bs4 import BeautifulSoup
from import_gis import import_gis
from data_sources import minWait

lastDatapointsUpdate = 0
name = "Germany"

def import_data():
    global lastDatapointsUpdate

    sourceLink = 'https://www.zeit.de/wissen/gesundheit/coronavirus-echtzeit-karte-deutschland-landkreise-infektionen-ausbreitung#karte'
    jsonURL = 'https://interactive.zeit.de/cronjobs/2020/corona/germany.json'

    jsonContent = requests.get(jsonURL, timeout=10).json()
    datapoints = []
    for state in jsonContent['states']['items']:
        stateStats = state['currentStats']
        datapoints.append({
            "country": "Germany",
            "province": state['name'],
            "total": stateStats['count'],
            "deaths": stateStats['dead'],
            "recovered": stateStats['recovered']
        })

    if upload.upload_datapoints(datapoints):
        lastDatapointsUpdate = time.time()
        
if __name__ == "__main__":
    import_data()