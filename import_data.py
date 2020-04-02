import pandas as pd
import corona_sql
import numpy as np
from datetime import date, timedelta
import time
import os
import requests
import web_app
import io

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
		
	for _, row in df.iterrows():
		country = row[country_col].strip()
		if "china" in country.lower():
			country = "China"  # normalizes "Mainland China"
		province = ''
		admin2 = ''
		
		if not pd.isnull(row[province_col]):
			province = row[province_col].strip()
		
		if admin2_col:
			if not pd.isnull(row[admin2_col]):
				admin2 = row[admin2_col].strip()
		
		confirmed = row[confirmed_col]
		dead = row[death_col]
		recovered = row[recovered_col]

		if np.isnan(confirmed): confirmed = 0
		if np.isnan(dead): dead = 0
		if np.isnan(recovered): recovered = 0

		active = confirmed - dead - recovered
		
		# save the location data if we can
		if lat_col in df.columns and lng_col in df.columns:
			lat, lng = row[lat_col], row[lng_col]
			if np.isnan(lat): lat = 0
			if np.isnan(lng): lng = 0

			if not (lat == 0 and lng == 0):
				location_data[country, province, admin2] = lat, lng
		
		data_points = add_to_dict(data_points, country, province, admin2, (confirmed, dead, recovered, active))

	print("\tFinished downloading and processing")
	print("\tUploading...")

	with web_app.app.app_context():
		for region, stats in data_points.items():
			country, province, admin2 = region
			confirmed, dead, recovered, active = stats
			
			active = confirmed - recovered - dead

			lat, lng = (0, 0)
			location_labelled = False

			if region in location_data:
				lat, lng = location_data[region]
				location_labelled = True

			yesterday_data = corona_sql.session.query(corona_sql.Datapoint).filter_by(
				entry_date=yesterday,
				
				admin2=admin2,
				province=province,
				country=country
			).all()

			yesterday_confirmed = yesterday_recovered = yesterday_dead = yesterday_active = 0
			is_first_day = True

			if yesterday_data:
				is_first_day = False
				datapoint = yesterday_data[0]

				yesterday_confirmed = datapoint.confirmed
				yesterday_recovered = datapoint.recovered
				yesterday_dead = datapoint.dead
				yesterday_active = datapoint.active

			new_data = corona_sql.Datapoint(
				entry_date=entry_date,
				
				admin2=admin2,
				province=province,
				country=country,
				
				latitude=lat,
				longitude=lng,

				location_labelled=location_labelled,
				is_first_day=is_first_day,
				
				confirmed=confirmed,
				dead=dead,
				recovered=recovered,
				active=active,

				dconfirmed=confirmed-yesterday_confirmed,
				ddead=dead-yesterday_dead,
				drecovered=recovered-yesterday_recovered,
				dactive=active-yesterday_active
			)

			corona_sql.session.add(new_data)
		
		corona_sql.session.commit()
		
		print(f"\tImported data for date {entry_date}")

def download_data_for_date(entry_date):
	date_formatted = entry_date.strftime("%m-%d-%Y")
	
	with web_app.app.app_context():
		existing_data = corona_sql.session.query(corona_sql.Datapoint).filter_by(entry_date=entry_date).all()
		if existing_data:
			print("\tEntries already made")
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
	time.sleep(5)
	
	add_date_range(date_1=date(2020, 3, 10), date_2=date.today())
	
	while True:
		status = download_data_for_date(date.today())
		
		if status == '404':
			time.sleep(60)

def add_date_range(date_1, date_2):
	next_date = timedelta(days=1)
	current_date = date_1
	while current_date <= date_2:
		result = download_data_for_date(current_date)
		if result == '404':
			return
		current_date += next_date

if __name__ == "__main__":
	data_download()
