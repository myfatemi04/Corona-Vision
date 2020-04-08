import pandas as pd
from corona_sql import *
import numpy as np
from datetime import date, timedelta
import time
import os
import requests
import web_app
import io
import locations

def add_tuple_values(a, b):
	return tuple(sum(x) for x in zip(a, b))

def add_to_dict(dct, country, province, admin2, value_list):
	
	# use a set so that if for example province = "", we don't add the values to (country, "", "") twice
	combinations = set(
		[
			(country, province, admin2),
			(country, province, ""),
			(country, "", ""),
			("", "", "")
		]
	)

	for combination in combinations:
		if combination not in dct:
			dct[combination] = value_list
		else:
			dct[combination] = add_tuple_values(dct[combination], value_list)

	return dct

def import_data(csv_text, entry_date):
	string_io = io.StringIO(csv_text)
	df = pd.read_csv(string_io)
	yesterday = entry_date + timedelta(days=-1)
	
	lat_col = lng_col = ""
	country_col = province_col = admin2_col = ""
	confirmed_col = death_col = recovered_col = ""
	
	for col in df.columns:
		if 'lat' in col.lower():
			lat_col = col
		elif 'long' in col.lower():
			lng_col = col
		elif 'country' in col.lower():
			country_col = col
		elif 'province' in col.lower():
			province_col = col
		elif 'admin2' in col.lower():
			admin2_col = col
		elif "death" in col.lower() or "dead" in col.lower():
			death_col = col
		elif "confirm" in col.lower():
			confirmed_col = col
		elif "recover" in col.lower():
			recovered_col = col
	
	data_points = {}
	location_data = {}
	accurate = set()
	primary = set()
		
	for _, row in df.iterrows():
		country = row[country_col].strip()
		if "china" in country.lower():
			country = "China"  # normalizes "Mainland China"
		if "korea" in country.lower():
			if "south" in country.lower():
				country = "South Korea"
			elif "republic" in country.lower():
				country = "South Korea"
			elif "north" in country.lower():
				country = "North Korea"
		
		if country.lower() == "uk":
			country = "United Kingdom"
		elif country.lower() == "us":
			country = "United States"
		
		if country.lower().endswith(", the"):
			country = country[:-len(", the")]

		if country.lower().startswith("republic of "):
			country = country[len("republic of "):]

		if "russia" in country.lower():
			country = "Russia"

		if country.lower().startswith("the "):
			country = country[len("the "):]

		if country.lower() == "viet nam":
			country = "Vietnam"

		country = country.replace(" (Islamic Republic Of)" , "")
		
		province = ''
		admin2 = ''
		
		if not pd.isnull(row[province_col]):
			province = row[province_col].strip()
		
		if admin2_col:
			if not pd.isnull(row[admin2_col]):
				admin2 = row[admin2_col].strip()
		
		if not admin2:
			if ", " in province and country.lower() in ['us', 'united states']:
				comma_index = province.rfind(", ")
				county, state_code = province[:comma_index], province[comma_index + 2:]
				admin2 = county
				province = locations.get_state_name("US", state_code) or state_code
				if province == 'D.C.':
					province = "District of Columbia"
		
		primary.add((country, province, admin2))
		
		confirmed = row[confirmed_col]
		deaths = row[death_col]
		recovered = row[recovered_col]

		if np.isnan(confirmed): confirmed = 0
		if np.isnan(deaths): deaths = 0
		if np.isnan(recovered): recovered = 0

		active = confirmed - deaths - recovered

		admin2_region = country, province, admin2
		province_region = country, province, ''
		country_region = country, '', ''

		# save the location data if we can
		if lat_col in df.columns and lng_col in df.columns:
			lat, lng = row[lat_col], row[lng_col]
			if np.isnan(lat): lat = 0
			if np.isnan(lng): lng = 0

			if not (lat == 0 and lng == 0):
				location_data[admin2_region] = lat, lng
				accurate.add(admin2_region)
		
		province_location = locations.get_location(country, province)
		if province_location:
			if province_region not in location_data:
				location_data[province_region] = province_location
				accurate.add(province_region)
			if admin2_region not in location_data:
				location_data[admin2_region] = province_location  # estimate to province location
			
		country_location = locations.get_location(country)
		if country_location:
			if country_region not in location_data:
				location_data[country_region] = country_location
				accurate.add(country_region)
			if province_region not in location_data:
				location_data[province_region] = country_location
			if admin2_region not in location_data:
				location_data[admin2_region] = country_location
		
		data_points = add_to_dict(data_points, country, province, admin2, (confirmed, deaths, recovered, active))

	print("\tFinished downloading and processing")
	print("\tUploading...")

	with web_app.app.app_context():
		session = db.session()
		for region, stats in data_points.items():
			country, province, admin2 = region
			confirmed, deaths, recovered, active = stats
			is_primary = region in primary

			active = confirmed - recovered - deaths

			lat, lng = (0, 0)
			location_labelled = region in location_data
			location_accurate = region in accurate

			if region in location_data:
				lat, lng = location_data[region]

			yesterday_data = session.query(Datapoint).filter_by(
				entry_date=yesterday,
				
				admin2=admin2,
				province=province,
				country=country
			).all()

			yesterday_confirmed = yesterday_recovered = yesterday_deaths = yesterday_active = 0
			is_first_day = True

			if yesterday_data:
				is_first_day = False
				datapoint = yesterday_data[0]

				yesterday_confirmed = datapoint.confirmed
				yesterday_recovered = datapoint.recovered
				yesterday_deaths = datapoint.deaths
				yesterday_active = datapoint.active

			new_data = Datapoint(
				entry_date=entry_date,
				
				admin2=admin2,
				province=province,
				country=country,
				
				latitude=lat,
				longitude=lng,

				location_labelled=location_labelled,
				location_accurate=location_accurate,
				is_first_day=is_first_day,
				is_primary=is_primary,
				
				confirmed=confirmed,
				deaths=deaths,
				recovered=recovered,
				active=active,

				dconfirmed=confirmed-yesterday_confirmed,
				ddeaths=deaths-yesterday_deaths,
				drecovered=recovered-yesterday_recovered,
				dactive=active-yesterday_active
			)

			session.add(new_data)
		
		session.commit()
		
		print(f"\tImported data for date {entry_date}")

def download_data_for_date(entry_date):
	date_formatted = entry_date.strftime("%m-%d-%Y")
	
	with web_app.app.app_context():
		session = db.session()
		existing_data = session.query(Datapoint).filter_by(entry_date=entry_date).all()
		if existing_data:
			print("\tEntries already made: ", date_formatted)
			return 'exists'

		print("[DATA IMPORT] Attempting to download " + str(entry_date))
		github_raw_url = f"https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{date_formatted}.csv"
		response = requests.get(github_raw_url)
		
		if response.status_code == 200:
			csv_text = response.text
			import_data(csv_text, entry_date)
			
			print("\tComplete")
			return 'done'
		else:
			print("\tDate not found")
			return '404'

# daily reports link: https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports
def data_download():
	time.sleep(2)
	
	add_date_range(date_1=date(2020, 1, 22), date_2=date.today())
	
	while True:
		status = download_data_for_date(date.today())
		
		if status == '404' or status == 'exists':
			time.sleep(60)

def add_date_range(date_1, date_2):
	next_date = timedelta(days=1)
	current_date = date_1
	while current_date <= date_2:
		result = download_data_for_date(current_date)
		if result == '404':
			return
		current_date += next_date

def fix_locations():
	with web_app.app.app_context():
		session = db.session()
		state_list = session.query(Datapoint.country, Datapoint.province).distinct()
		for country, province in state_list:
			location = locations.get_location(country, province)
			if location:
				latitude, longitude = location
				session.query(Datapoint).filter(
					Datapoint.country==country,
					Datapoint.province==province,
					Datapoint.location_labelled==False
				).update(
					dict(
						location_labelled=True,
						latitude=latitude,
						longitude=longitude
					)
				)

				print("Updated ", country, province, " to ", latitude, longitude)
		session.commit()

if __name__ == "__main__":
	pass # fix_locations()
