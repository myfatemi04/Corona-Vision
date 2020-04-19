import pandas as pd
import numpy as np
import io
from corona_sql import Session, Datapoint
from import_data import bno_countries
from datetime import timedelta, date
import standards
import requests

def import_csv_data(csv_text, entry_date):
	# load the CSV data
	string_io = io.StringIO(csv_text)
	df = pd.read_csv(string_io)
	
	# define the columns
	lat_col = lng_col = ""
	admin0_col = admin1_col = admin2_col = ""
	total_col = death_col = recovered_col = ""
	
	# future-proofing
	for col in df.columns:
		if 'lat' in col.lower(): lat_col = col
		elif 'long' in col.lower(): lng_col = col
		elif 'country' in col.lower(): admin0_col = col
		elif 'province' in col.lower(): admin1_col = col
		elif 'admin2' in col.lower(): admin2_col = col
		elif "death" in col.lower(): death_col = col
		elif "dead" in col.lower(): death_col = col
		elif "confirm" in col.lower(): total_col = col
		elif "recover" in col.lower(): recovered_col = col
	
	data_points = []

	df.sort_values(by=[col for col in [admin2_col, admin1_col, admin0_col] if col], ascending=False)
	
	for _, row in df.iterrows():
		# Steps
		# 1. Find country, province, and county name
		# 2. Get the actual coronavirus numbers
		# 3. Estimate the location if we can

		# STEP 1 #
		admin0 = standards.fix_admin0_name(row[admin0_col].strip())

		# DEBUG MARKER
		# THIS IS ONLY BECAUSE WE HAVE BNO NEWS
		# if admin0 in bno_countries:
		# 	print("\rSkipping data from " + admin0, end='\r')
		# 	continue
	
		admin1 = '' if pd.isnull(row[admin1_col]) else row[admin1_col]
		admin2 = ''
		
		if not pd.isnull(row[admin1_col]):
			admin1 = row[admin1_col].strip()
		
		if admin2_col and not pd.isnull(row[admin2_col]):
			admin2 = row[admin2_col].strip()
			if admin2.lower().endswith(" county"):
				admin2 = admin2[:-len(" county")]
		else:
			# This is for old data
			# Some points have their admin1 listed as "Chicago, IL" or etc
			# The admin2 should be "Chicago", and the state should be "IL"
			if ', ' in admin1 and admin0 == 'United States':
				admin2, admin1 = standards.get_admin2_admin1(admin0, admin1)
		
		# STEP 2 #
		total = row[total_col]
		deaths = row[death_col]
		recovered = row[recovered_col]

		if np.isnan(total): total = 0
		if np.isnan(deaths): deaths = 0
		if np.isnan(recovered): recovered = 0

		row = {
			"admin0": admin0,
			"admin1": admin1,
			"admin2": admin2,
			"total": total,
			"deaths": deaths,
			"recovered": recovered,
		}

		# Save the primary location data if we can
		if lat_col and lng_col:
			lat, lng = row[lat_col], row[lng_col]
			if not np.isnan(lat) and not np.isnan(lng):
				row['latitude'] = lat
				row['longitude'] = lng

		data_points.append(row)
		
	return data_points

def download_data_for_date(entry_date):
	date_formatted = entry_date.strftime("%m-%d-%Y")
	print("\rLoading data from JHU " + date_formatted + '...', end='\r')
	
	# download from Github
	github_raw_url = f"https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{date_formatted}.csv"
	response = requests.get(github_raw_url)
	
	if response.status_code != 200:
		return None

	csv_text = response.text
	return import_csv_data(csv_text, entry_date)

def add_date_range(date_1, date_2):
	next_date = timedelta(days=1)
	current_date = date_1
	acc = []
	while current_date <= date_2:
		result = download_data_for_date(current_date)
		if not result:
			return
		acc += result
		current_date += next_date
	return acc