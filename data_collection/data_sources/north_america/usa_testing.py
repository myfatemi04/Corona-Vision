import requests
import json_extractor
import standards
from data_sources import source

@source('live', name='USA Testing')
def import_data():
	
	rq = requests.get("https://covidtracking.com/api/v1/states/current.json", timeout=10)
	j = rq.json()
	for row in j:
		yield {
			'country': 'United States',
			'province': standards.state_codes['United States'][row['state']],
			'tests': row['totalTestResults'] or 0,
			'hospitalized': row['hospitalizedCurrently'] or 0,
			'recovered': row['recovered'] or 0
		}

@source('historical', name='USA Testing')
def import_historical_data():
	from data_parser import import_json
	print("Uploading historical USA testing data...")
	results = import_json(
		url="https://covidtracking.com/api/v1/states/daily.json",
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