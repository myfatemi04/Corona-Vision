import requests
import time
import upload
from import_gis import import_gis
from data_parser import import_df

lastDatapointsUpdate = 0
minWait = 600

def import_data():
	global lastDatapointsUpdate

	import_provinces()
	import_counties()

def import_counties():
	print("Loading from Italy counties...")
	global lastDatapointsUpdate
	import io
	import pandas as pd
	import datetime
	csvSource = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-province/dpc-covid19-ita-province-latest.csv"
	sourceLink = "https://github.com/pcm-dpc/COVID-19/blob/master/dati-province/dpc-covid19-ita-province-latest.csv"

	rq = requests.get(csvSource)
	dataframe = pd.read_csv(io.StringIO(rq.text))

	datapoints = []
	locations = []
	for _, row in dataframe.iterrows():
		date, _, _, province, _, county, _, latitude, longitude, total, _, _ = row
		locations.append({
			"country": "Italy",
			"province": province,
			"county": county,
			"latitude": latitude,
			"longitude": longitude
		})
		datapoints.append({
			"country": "Italy",
			"province": province,
			"county": county,
			"total": total,
			# "entry_date": datetime.datetime.strptime(date[:10], "%Y-%m-%d").date()
		})

	overall = {
		'datapoint': datapoints,
		'location': locations,
		'source_link': sourceLink
	}

	if upload.upload(overall):
		lastDatapointsUpdate = time.time()

def import_provinces():
	print("Loading from Italy provinces...")
	global lastDatapointsUpdate
	import io
	import pandas as pd
	import datetime
	csvSource = "https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni-latest.csv"
	sourceLink = "https://github.com/pcm-dpc/COVID-19/blob/master/dati-regioni/dpc-covid19-ita-regioni-latest.csv"

	rq = requests.get(csvSource)
	dataframe = pd.read_csv(io.StringIO(rq.text))

	datapoints = []
	locations = []
	for _, row in dataframe.iterrows():
		# Hospitalized != Hospitalized with symptoms
		date, countryCode, provinceCode, province, latitude, longitude, hosp_symptoms, serious, hospitalized, homeIsolation, activeCases, variationActive, newActive, recovered, deaths, total, swabs, caseTests, noteIt, noteEn = row
		locations.append({
			"country": "Italy",
			"province": province,
			"latitude": latitude,
			"longitude": longitude
		})
		datapoints.append({
			"country": "Italy",
			"province": province,
			"total": total,
			"serious": serious,
			"hospitalized": hospitalized,
			"recovered": recovered,
			"deaths": deaths,
			"tests": caseTests,
			# "entry_date": datetime.datetime.strptime(date[:10], "%Y-%m-%d").date()
		})

	overall = {
		'datapoint': datapoints,
		'location': locations,
		'source_link': sourceLink
	}

	if upload.upload(overall):
		lastDatapointsUpdate = time.time()

