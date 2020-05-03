import requests
import time
import upload
from import_gis import import_geojson
from data_sources import minWait
from datetime import datetime

lastDatapointsUpdate = 0

def import_data():
	global lastDatapointsUpdate

	results = import_geojson(
		query_url="https://opendata.arcgis.com/datasets/628578697fb24d8ea4c32fa0c5ae1843_0.geojson",
		table_labels={
			"location": {
				"country": ["Country_Region"],
				"province": ["Province_State"],
				"county": ["Admin2"],
				"latitude": ["Lat"],
				"longitude": ["Long_"]
			},
			"datapoint": {
				"country": ["Country_Region"],
				"province": ["Province_State"],
				"county": ["Admin2"],
				"total": ["Confirmed"],
				"recovered": ["Recovered"],
				"deaths": ["Deaths"]
			}
		}
	)

	if upload.upload(results):
		lastDatapointsUpdate = time.time()

def import_hist():
	pass

def import_hist_states():
	stateList = requests.get("https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv").text
	#"https://github.com/nytimes/covid-19-data"
	datapoints = []
	for row in stateList.split("\n")[1:]:
		dateStr, province, fips, cases, deaths = row.split(",")
		if dateStr > '2020-04-20':
			datapoints.append({
				'entry_date': datetime.strptime(dateStr, "%Y-%m-%d").date(),
				'country': 'United States',
				'province': province,
				'total': int(cases),
				'deaths': int(deaths)
			})
	print(f"Uploading {len(datapoints)} historical datapoints")
	upload.upload_datapoints(datapoints)

def import_hist_counties():
	countyList = requests.get("https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv").text
	datapoints = []
	for row in countyList.split("\n")[1:]:
		dateStr, county, province, fips, cases, deaths = row.split(",")
		if dateStr > '2020-04-28':
			datapoints.append({
				'entry_date': datetime.strptime(dateStr, "%Y-%m-%d").date(),
				'country': 'United States',
				'province': province,
				'county': county,
				'total': int(cases),
				'deaths': int(deaths)
			})
	print(f"Uploading {len(datapoints)} historical datapoints")
	upload.upload_datapoints(datapoints)


def import_uk():
	#"https://github.com/tomwhite/covid-19-uk-data/tree/master/data"
	ukSeries = requests.get("https://raw.githubusercontent.com/tomwhite/covid-19-uk-data/master/data/covid-19-totals-uk.csv").text
	datapoints = []
	for row in ukSeries.split("\n")[1:]:
		if row:
			dateStr, tests, cases, deaths = row.split(",")
			if dateStr > '2020-04-20':
				datapoints.append({
					'entry_date': datetime.strptime(dateStr, "%Y-%m-%d").date(),
					'country': 'United Kingdom',
					'total': int(cases),
					'deaths': int(deaths),
					'tests': int(tests)
				})
	print(f"Uploading {len(datapoints)} historical datapoints")
	upload.upload_datapoints(datapoints)