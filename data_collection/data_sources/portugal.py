import requests
import time
import upload
from data_imports.import_gis import import_gis
from data_sources import minWait

lastDatapointsUpdate = 0

def import_data():
	global lastDatapointsUpdate

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