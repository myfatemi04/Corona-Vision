import requests
import time
import upload
from import_gis import import_gis
from data_sources import minWait

lastDatapointsUpdate = 0
def import_data():
	global lastDatapointsUpdate
	if time.time() - lastDatapointsUpdate < minWait:
		print("Not uploading Netherlands because elapsed < minWait")
		return
	else:
		print("Loading from Netherlands...")

	results = import_gis(
		"https://services.arcgis.com/nSZVuSZjHpEZZbRo/arcgis/rest/services/Coronavirus_RIVM_vlakken_actueel/FeatureServer/0//",
		table_labels={
			"datapoint": {
				"country": "Netherlands",
				"province": ["Provincie"],
				"county": ["Gemeentenaam"],
				"total": ["Meldingen"],
				"hospitalized": ["Ziekenhuisopnamen"],
				"deaths": ["Overleden"]
			},
			"location": {
				"country": "Netherlands",
				"province": ["Provincie"],
				"county": ["Gemeentenaam"],
				"population": ["Bevolkingsaantal", "::dividethousands"]
			}
		}
	)

	if upload.upload(results):
		lastDatapointsUpdate = time.time()

