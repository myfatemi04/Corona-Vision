import requests
import json_extractor
import upload
import time
from bs4 import BeautifulSoup
from import_gis import import_gis
from data_sources import minWait

lastDatapointsUpdate = 0
name = "Brazil"

def import_data():
    global lastDatapointsUpdate

    headers = {
        'x-parse-application-id': 'unAFkcaNDeXajurGB7LChj8SgQYS2ptm'
    }

    jsonURL = "https://xx9p7hp1p7.execute-api.us-east-1.amazonaws.com/prod/PortalMapa"
    sourceURL = "https://covid.saude.gov.br/"

    content = requests.get(jsonURL, headers=headers, timeout=10).json()
    datapoints = []
    locations = []

    for row in content['results']:
        datapoints.append({
            "country": "Brazil",
            "province": row['nome'],
            "total": row['qtd_confirmado'],
            "deaths": row['qtd_obito']
        })

        locations.append({
            "country": "Brazil",
            "province": row['nome'],
            "latitude": row['latitude'],
            "longitude": row['longitude']
        })

    upload.upload_locations(locations)
    if upload.upload_datapoints(datapoints):
        lastDatapointsUpdate = time.time()

if __name__ == "__main__":
    import_data()