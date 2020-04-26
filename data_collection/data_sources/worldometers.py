import requests
import time
import upload
import standards
from data_parser import import_table

lastDatapointsUpdate = 0
minWait = 60

disallowed = {
	"United States": ["tests"],
	"Albania": [],
	"India": [],
	"Japan": []
}

def import_data():
	global lastDatapointsUpdate
	if time.time() - lastDatapointsUpdate < minWait:
		print("Not uploading because elapsed < minWait")
		return
	else:
		print("Loading from Worldometers...")

	results = import_table(
		"http://www.worldometers.info/coronavirus",
		["#main_table_countries_today", 0],
		{
			"datapoint": {
				"country": ["Country,  Other"],
				"total": ["Total  Cases", "::number"],
				"deaths": ["Total  Deaths", "::number"],
				"serious": ["Serious,  Critical", "::number"],
				"tests": ["Total  Tests", "::number"],
				"recovered": ["Total  Recovered", "::number"]
			}
		}
	)

	def delif(result, key):
		if key in result:
			del result[key]
	
	for result in results['datapoint']:
		result['country'], _, _ = standards.normalize_name(result['country'], '', '')
		if result['country'] in disallowed:
			features = disallowed[result['country']] or ['total', 'deaths']
			for feature in features:
				delif(result, feature)

	if upload.upload(results):			
		lastDatapointsUpdate = time.time()
