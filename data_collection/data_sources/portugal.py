import requests
from data_imports.import_gis import import_gis
from data_sources import source

@source('live', name='Portugal')
def import_data():
	for result in import_gis(
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
	):
		yield result