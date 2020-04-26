import requests
import time
import upload
from import_gis import import_gis

lastDatapointsUpdate = 0
minWait = 60 * 15

def import_data():
    global lastDatapointsUpdate
    if time.time() - lastDatapointsUpdate < minWait:
        print("Not uploading South Korea because elapsed < minWait")
        return
    else:
        print("Loading from South Korea...")

    results = import_gis(
		"https://services2.arcgis.com/RiHDI9SnFmD3Itzs/arcgis/rest/services/%EC%8B%9C%EB%8F%84%EB%B3%84_%EC%BD%94%EB%A1%9C%EB%82%98/FeatureServer/0/",
		{
			"location": {
				"country": "South Korea",
				"province": ["CTP_ENG_NM"]
			},
			"datapoint": {
				"country": "South Korea",
				"province": ["CTP_ENG_NM"],
				"total": ["발생자수"],
				"deaths": ["사망자수"],
			}
		}
	)

    if upload.upload(results):
    	lastDatapointsUpdate = time.time()