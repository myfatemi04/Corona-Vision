import requests
import json_extractor
import upload
import time
import upload
from import_gis import import_gis
from data_sources import minWait

lastDatapointsUpdate = 0

def import_data():
    global lastDatapointsUpdate

    results = import_gis(
        gis_url="https://utility.arcgis.com/usrsvcs/servers/83b36886c90942ab9f67e7a212e515c8/rest/services/Corona/DailyCasesMoHUA/MapServer/0/",
        table_labels={
            "datapoint": {
                "country": "India",
                "province": ["state_name"],
                "total": ["confirmedcases"],
                "recovered": ["cured_discharged_migrated"],
                "deaths": ["deaths"]
            }
        },
        use_geometry=False
    )

    if upload.upload(results):
        lastDatapointsUpdate = time.time()