import requests
import upload
import time
from data_sources import minWait

lastDatapointsUpdate = 0
name = "Australia"

def import_data():
    global lastDatapointsUpdate

    url = "https://redutv-api.vg.no/corona/v1/sheets/norway-region-data?exclude=cases"
    json = requests.get(url).json()
    country_data = json['metadata']
    datapoint = {
        'country': 'Norway',
        'total': country_data['confirmed']['total'],
        'deaths': country_data['dead']['total']
    }

    if upload.upload_datapoints([datapoint]):
        lastDatapointsUpdate = time.time()

if __name__ == "__main__":
    import_data()