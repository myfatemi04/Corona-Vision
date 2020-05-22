import requests
import time
import upload
from data_imports.import_gis import import_gis
from data_sources import minWait

lastDatapointsUpdate = 0
def import_data():
	global lastDatapointsUpdate

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

