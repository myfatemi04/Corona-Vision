import pandas as pd
import numpy as np
import io
from corona_sql import Session, Datapoint, upload, generate_location_map
from datetime import timedelta, date
import standards
import requests

def add_tuple_values(a, b):
	return tuple(sum(x) for x in zip(a, b))

def add_to_dict(dct, country, province, admin2, value_list):
	
	# use a set so that if for example province = "", we don't add the values to (country, "", "") twice
	combinations = {
		(country, province, admin2),
		(country, province, ""),
		(country, "", ""),
		("", "", "")
	}

	for combination in combinations:
		if combination not in dct:
			dct[combination] = value_list
		else:
			dct[combination] = add_tuple_values(dct[combination], value_list)

	return dct

def import_data(csv_text, entry_date):
	# load the CSV data
	string_io = io.StringIO(csv_text)
	df = pd.read_csv(string_io)
	
	# define the columns
	lat_col = lng_col = ""
	country_col = province_col = admin2_col = ""
	confirmed_col = death_col = recovered_col = ""
	
	# future-proofing
	for col in df.columns:
		if 'lat' in col.lower(): lat_col = col
		elif 'long' in col.lower(): lng_col = col
		elif 'country' in col.lower(): country_col = col
		elif 'province' in col.lower(): province_col = col
		elif 'admin2' in col.lower(): admin2_col = col
		elif "death" in col.lower(): death_col = col
		elif "dead" in col.lower(): death_col = col
		elif "confirm" in col.lower(): confirmed_col = col
		elif "recover" in col.lower(): recovered_col = col
	
	data_points = {}
	location_data = {}
	primary = set()

	df.sort_values(by=[admin2_col, country_col, province_col], ascending=False)
	
	for _, row in df.iterrows():
		# Steps
		# 1. Find country, province, and county name
		# 2. Get the actual coronavirus numbers
		# 3. Estimate the location if we can

		# STEP 1 #
		country = standards.fix_country_name(row[country_col].strip())
		province = '' if pd.isnull(row[province_col]) else row[province_col]
		admin2 = ''
		
		if not pd.isnull(row[province_col]):
			province = row[province_col].strip()
		
		if admin2_col and not pd.isnull(row[admin2_col]):
			admin2 = row[admin2_col].strip()
			if admin2.lower().endswith(" county"):
				admin2 = admin2[:-len(" county")]
		else:
			# This is for old data
			# Some points have their province listed as "Chicago, IL" or etc
			# The admin2 should be "Chicago", and the state should be "IL"
			if ', ' in province and country == 'United States':
				admin2, province = standards.get_admin2_province(country, province)
		
		primary.add((country, province, admin2))
		
		# STEP 2 #
		confirmed = row[confirmed_col]
		deaths = row[death_col]
		recovered = row[recovered_col]

		if np.isnan(confirmed): confirmed = 0
		if np.isnan(deaths): deaths = 0
		if np.isnan(recovered): recovered = 0

		active = confirmed - deaths - recovered

		region = country, province, admin2

		# Save the primary location data if we can
		if lat_col and lng_col:
			lat, lng = row[lat_col], row[lng_col]
			if not np.isnan(lat) and not np.isnan(lng):
				if lat != 0 or lng != 0:
					location_data[region] = lat, lng, True
		
		data_points = add_to_dict(data_points, country, province, admin2, (confirmed, deaths, recovered, active))

		# if countries are repeated, then this will fix it
		data_points[country, province, admin2] = (confirmed, deaths, recovered, active)

	session = Session() # for looking at yesterday's data
	yesterday = entry_date + timedelta(days=-1)
	yesterday_points = session.query(Datapoint).filter_by(entry_date=yesterday.isoformat())
	yesterday_map = {pt.location_tuple(): pt for pt in yesterday_points}
	DATA_ROWS = []
	for region, stats in data_points.items():
		country, province, admin2 = region

		confirmed, deaths, recovered, active = stats
		is_primary = region in primary

		active = confirmed - recovered - deaths

		if region in location_data:
			lat, lng, _ = location_data[region]
		else:
			estimated_location = standards.get_estimated_location(*region)

			if estimated_location['accurate']:
				lat, lng = estimated_location['location']

		# See if we have data from yesterday to compare to

		dconfirmed = confirmed
		drecovered = recovered
		ddeaths = deaths
		dactive = active

		if region in yesterday_map:
			yesterday_data = yesterday_map[region]
			is_first_day = False

			dconfirmed -= yesterday_data.confirmed
			drecovered -= yesterday_data.recovered
			ddeaths -= yesterday_data.deaths
			dactive -= yesterday_data.active
		else:
			is_first_day = True

		data_row = {
			"admin2": admin2, "province": province, "country": country,
			"latitude": lat, "longitude": lng,
			"is_first_day": is_first_day, "is_primary": is_primary,
			"confirmed": confirmed, "deaths": deaths, "recovered": recovered, "active": active,
			"dconfirmed": dconfirmed, "ddeaths": ddeaths, "drecovered": drecovered, "dactive": dactive,
			"entry_date": entry_date.isoformat()
		}

		DATA_ROWS.append(data_row)
	
	print("\rUploading", end='\r')
	upload(DATA_ROWS, {"entry_date": entry_date.isoformat()}, source_link="https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports")
	print(f"\rImported data for date {entry_date}")

def download_data_for_date(entry_date):
	session = Session()

	existing_data = session.query(Datapoint).filter_by(
		entry_date=entry_date.isoformat(),
		is_primary=True).first() # first() has a limit of one result, so it's efficient

	date_formatted = entry_date.strftime("%m-%d-%Y")
	print("\rAttempting to download " + date_formatted + '...', end='')
	
	# don't do it again
	if existing_data:
		print("data already exists", end='')
		return -1

	# download from Github
	github_raw_url = f"https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{date_formatted}.csv"
	response = requests.get(github_raw_url)
	
	if response.status_code != 200:
		print("date not found	   ", end='')
		return 404

	csv_text = response.text
	import_data(csv_text, entry_date)
	return 200

def add_date_range(date_1, date_2):
	next_date = timedelta(days=1)
	current_date = date_1
	while current_date <= date_2:
		if download_data_for_date(current_date) == 404:
			return
		current_date += next_date