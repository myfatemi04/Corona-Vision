import requests
import json_extractor
import upload
import time
import upload
from data_parser import import_json
from data_sources import minWait

lastDatapointsUpdate = 0

def import_data():
    global lastDatapointsUpdate
    if time.time() - lastDatapointsUpdate < minWait:
        print("Not uploading Japan because elapsed < minWait")
        return
    else:
        print("Loading from Japan...")

    datapoints = []
    j = requests.get("https://data.covid19japan.com/summary/latest.json").json()
    for row in j['prefectures']:
        datapoints.append({
            "country": "Japan",
            "province": row['name'],
            "total": row['confirmed'],
            "deaths": row['deaths'],
            "recovered": row['recovered']
        })
    
    if upload.upload_datapoints(datapoints, "https://covid19japan.com/"):
        lastDatapointsUpdate = time.time()