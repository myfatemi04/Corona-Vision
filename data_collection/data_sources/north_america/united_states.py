import requests
from data_imports.import_gis import import_geojson
from datetime import datetime
from data_sources import source

@source('live', name='United States')
def import_data():
	return import_geojson(
		query_url="https://opendata.arcgis.com/datasets/628578697fb24d8ea4c32fa0c5ae1843_0.geojson",
		table_labels={
			"datapoint": {
				"country": ["Country_Region"],
				"province": ["Province_State"],
				"county": ["Admin2"],
				"total": ["Confirmed"],
				"recovered": ["Recovered"],
				"deaths": ["Deaths"]
			}
		})['datapoint']

@source('historical', 'us-states', name="United States Historical")
def import_hist_states():
	stateList = requests.get("https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv", timeout=10).text
	#"https://github.com/nytimes/covid-19-data"
	datapoints = []
	for row in stateList.split("\n")[1:]:
		dateStr, province, fips, cases, deaths = row.split(",")
		if dateStr > '2020-04-20':
			yield {
				'entry_date': datetime.strptime(dateStr, "%Y-%m-%d").date(),
				'country': 'United States',
				'province': province,
				'total': int(cases),
				'deaths': int(deaths)
			}
	print(f"Uploading {len(datapoints)} historical datapoints")

@source('historical', 'us-counties', name='United States Counties Historical')
def import_hist_counties():
	countyList = requests.get("https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv", timeout=10).text

	for row in countyList.split("\n")[1:]:
		dateStr, county, province, fips, cases, deaths = row.split(",")
		if dateStr > '2020-05-20':
			yield {
				'entry_date': datetime.strptime(dateStr, "%Y-%m-%d").date(),
				'country': 'United States',
				'province': province,
				'county': county,
				'total': int(cases),
				'deaths': int(deaths)
			}


def import_uk():
	#"https://github.com/tomwhite/covid-19-uk-data/tree/master/data"
	ukSeries = requests.get("https://raw.githubusercontent.com/tomwhite/covid-19-uk-data/master/data/covid-19-totals-uk.csv", timeout=10).text
	datapoints = []
	for row in ukSeries.split("\n")[1:]:
		if row:
			dateStr, tests, cases, deaths = row.split(",")
			if dateStr > '2020-04-20':
				yield {
					'entry_date': datetime.strptime(dateStr, "%Y-%m-%d").date(),
					'country': 'United Kingdom',
					'total': int(cases),
					'deaths': int(deaths),
					'tests': int(tests)
				}
	print(f"Uploading {len(datapoints)} historical datapoints")
	upload.upload_datapoints(datapoints)