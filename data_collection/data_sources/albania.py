import requests
import json_extractor
import upload
import time
from data_sources import minWait

lastDatapointsUpdate = 0
name = "Albania"

def import_data():
    global lastDatapointsUpdate

    rq = requests.get('https://coronavirus.al/api/qarqet.php')
    j = rq.json()
    datapoints = []
    locations = []
    for row in j:
        datapoints.append({
            'country': 'Albania',
            'province': row['qarku'],
            'total': int(row['raste_gjithsej']),
            'recovered': int(row['sheruar']),
            'deaths': int(row['vdekur']),
            'serious': int(row['terapi_int']),
            'hospitalized': int(row['mjekim_spitalor']),
            'tests': int(row['teste'])
        })
        locations.append({
            'country': 'Albania',
            'province': row['qarku'],
            'latitude': float(row['lat']),
            'longitude': float(row['lon'])
        })
    
    if upload.upload_datapoints(datapoints, 'https://coronavirus.al/statistika/'):
        lastDatapointsUpdate = time.time()
        
    upload.upload_locations(locations)
