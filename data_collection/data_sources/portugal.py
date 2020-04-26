import requests
import time
import upload
from import_gis import import_gis

lastDatapointsUpdate = 0
minWait = 60 * 15

def import_data():
	global lastDatapointsUpdate
	if time.time() - lastDatapointsUpdate < minWait:
		print("Not uploading Portugal because elapsed < minWait")
		return
	else:
		print("Loading from Portugal...")

	results = import_gis(
		"http://services.arcgis.com/CCZiGSEQbAxxFVh3/ArcGIS/rest/services/COVID19_Concelhos_V/FeatureServer/0/",
		{
			"location": {
				"country": "Portugal",
				"province": ["Distrito", "::cap"],
				"county": ["Concelho", "::cap"]
			},
			"datapoint": {
				"country": "Portugal",
				"province": ["Distrito", "::cap"],
				"county": ["Concelho", "::cap"],
				"deaths": ["Obitos_Conc"],
				"recovered": ["Recuperados_Conc"],
				"total": ["ConfirmadosAcumulado_Conc"]
			}
		}
	)

	if upload.upload(results):
		lastDatapointsUpdate = time.time()