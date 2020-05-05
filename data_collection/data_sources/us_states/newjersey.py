import requests
import upload
import time
from data_sources import minWait

lastDatapointsUpdate = 0

def import_data():
    global lastDatapointsUpdate

    queryURL = "https://services7.arcgis.com/Z0rixLlManVefxqY/arcgis/rest/services/DailyCaseCounts/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&outFields=*"
    sourceURL = "https://www.nj.gov/health/cd/topics/covid2019_dashboard.shtml"

    json = requests.get(queryURL, timeout=10).json()
    datapoints = []

    for feature in json['features']:
        attr = feature['attributes']
        datapoints.append({
            "country": "United States",
            "province": "New Jersey",
            "county": attr['COUNTY'].capitalize(),
            "total": attr['TOTAL_CASES'],
            "deaths": attr['TOTAL_DEATHS'],
        })
    
    if upload.upload_datapoints(datapoints):
        lastDatapointsUpdate = time.time()

if __name__ == "__main__":
    import_data()