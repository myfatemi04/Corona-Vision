import pandas as pd
import numpy as np
import io
from upload import upload
from datetime import timedelta, date
import requests

def import_csv_data(csv_text, entry_date):
	# load the CSV data
	string_io = io.StringIO(csv_text)
	df = pd.read_csv(string_io, keep_default_na=False, na_values=['___'])
	
	# define the columns
	lat_col = lng_col = ""
	country_col = admin1_col = county_col = ""
	total_col = death_col = recovered_col = ""
	
	# future-proofing
	for col in df.columns:
		if 'lat' in col.lower(): lat_col = col
		elif 'long' in col.lower(): lng_col = col
		elif 'country' in col.lower(): country_col = col
		elif 'province' in col.lower(): admin1_col = col
		elif 'county' in col.lower(): county_col = col
		elif "death" in col.lower(): death_col = col
		elif "dead" in col.lower(): death_col = col
		elif "confirm" in col.lower(): total_col = col
		elif "recover" in col.lower(): recovered_col = col
	
	content = {
		'datapoint': [],
		'location': [],
		'source_link': "https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports"
	}

	df.sort_values(by=[col for col in [county_col, admin1_col, country_col] if col], ascending=False)
	
	for _, row in df.iterrows():
		# Steps
		# 1. Find country, province, and county name
		# 2. Get the actual coronavirus numbers
		# 3. Estimate the location if we can

		# STEP 1 #
		country = row[country_col]
		admin1 = row[admin1_col] if not pd.isnull(row[admin1_col]) else ''
		county = row[county_col] if county_col else ''

		# STEP 2 #
		total = row[total_col]
		deaths = row[death_col]
		recovered = row[recovered_col]

		if not total: total = 0
		if not deaths: deaths = 0
		if not recovered: recovered = 0

		location_row = {}
		datapoint_row = {}

		if admin1 == 'Recovered':
			datapoint_row = {
				"country": country,
				"recovered": recovered,
				"entry_date": entry_date
			}

			location_row = { "country": country }
		else:
			datapoint_row = {
				"country": country,
				"admin1": admin1,
				"county": county,
				"total": total,
				"deaths": deaths,
				"recovered": recovered,
				"entry_date": entry_date
			}

			location_row = {
				"country": country,
				"admin1": admin1,
				"county": county
			}

		# Save the primary location data if we can
		if lat_col and lng_col:
			lat, lng = row[lat_col], row[lng_col]
			if lat and lng:
				location_row['latitude'] = lat
				location_row['longitude'] = lng

		content['location'].append(location_row)
		content['datapoint'].append(datapoint_row)
	return content

def import_jhu_date(entry_date):
	date_formatted = entry_date.strftime("%m-%d-%Y")
	print("\rLoading data from JHU " + date_formatted + '...', end='\r')
	
	# download from Github
	github_raw_url = f"https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{date_formatted}.csv"
	response = requests.get(github_raw_url)
	
	if response.status_code == 200:
		return import_csv_data(response.text, entry_date)
	else:
		print("404 not found")

def import_jhu_date_range(date_1, date_2):
	next_date = timedelta(days=1)
	current_date = date_1
	
	while current_date <= date_2:
		print("Loading JHU data for", current_date, "                                      ")
		result = import_jhu_date(current_date)
		if result:
			yield result
		current_date += next_date

def import_jhu_historical():
	return import_jhu_date_range(date_1=date(2020, 4, 9), date_2=date.today())
