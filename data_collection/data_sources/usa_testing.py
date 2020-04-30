import requests
import json_extractor
import upload
import time
import standards
from data_sources import minWait

lastDatapointsUpdate = 0

def import_data():
	global lastDatapointsUpdate

	rq = requests.get("https://covidtracking.com/api/v1/states/current.json")
	j = rq.json()
	datapoints = []
	locations = []
	for row in j:
		datapoints.append({
			'country': 'United States',
			'province': standards.get_province_name("United States", row['state']),
			'tests': row['totalTestResults'] or 0,
			'hospitalized': row['hospitalizedCurrently'] or 0,
			'recovered': row['recovered'] or 0
		})
	
	if upload.upload_datapoints(datapoints, "https://covidtracking.com"):
		lastDatapointsUpdate = time.time()

	upload.upload_locations(locations)


def import_historical_data():
	from data_parser import import_json
	print("Uploading historical USA testing data...")
	results = import_json(
		url="https://covidtracking.com/api/v1/states/daily.json",
		source_link="https://covidtracking.com",
		table_labels={
			"datapoint": {
				"entry_date": ["date", "::str", "::ymd"],
				"country": "United States",
				"province": ["state", "::us_state_code"],
				"tests": ["total"],
				"hospitalized": ["hospitalized"],
				"recovered": ["recovered"]
			}
		},
		namespace=[]
	)

	upload.upload(results)