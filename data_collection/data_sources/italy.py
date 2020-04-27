import requests
import time
import upload
from import_gis import import_gis
from data_parser import import_json
from data_sources import minWait

lastDatapointsUpdate = 0

def import_data():
	global lastDatapointsUpdate
	if time.time() - lastDatapointsUpdate < minWait:
		print("Not uploading Italy because elapsed < minWait")
		return
	else:
		print("Loading from Italy...")

	results = import_gis(
		"https://services6.arcgis.com/L1SotImj1AAZY1eK/arcgis/rest/services/dpc_regioni_covid19/FeatureServer/0/",
		{
			"location" :{
				"country": "Italy",
				"province": ["denominazione_regione"],
				"latitude": ["latitudine"],
				"longitude": ["longitudine"],
			},
			"datapoint": {
				"country": "Italy",
				"province": ["denominazione_regione"],
				"total": ["totale_casi"],
				"deaths": ["deceduti"]
			}
		}
	)

	if upload.upload(results):
		lastDatapointsUpdate = time.time()

def import_historical_data():
	global lastDatapointsUpdate
	if time.time() - lastDatapointsUpdate < minWait:
		print("Not uploading because elapsed < minWait")
		return
	else:
		print("Loading from Italy...")

	results = import_json(
		url="https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-json/dpc-covid19-ita-province.json",
		source_link='https://github.com/pcm-dpc/COVID-19/',
		table_labels={
			"datapoint": {
				"country": "Italy",
				"entry_date": ["data", "::date_t"],
				"province": ["denominazione_regione"],
				"county": ["denominazione_provincia"],
				"total": ["totale_casi"]
			}
		},
		namespace=[]
	)

	upload.upload(results)