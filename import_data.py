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
	dataframe = pd.read_csv(string_io)
	
	lat_col = ""
	lng_col = ""
	country_col = ""
	province_col = ""
	admin2_col = ""
	
	for col in dataframe.columns:
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
			
	if not lat_col or not lng_col:
		print("\tNo latitude or longitude data")
		return
	
	data_points = {}
		
	for _, row in dataframe.iterrows():
		country = row[country_col]
		province = ''
		admin2 = ''
		
		if not pd.isnull(row[province_col]):
			province = row[province_col]
		
		if admin2_col:
			if not pd.isnull(row[admin2_col]):
				admin2 = row[admin2_col]
		
		confirmed = row['Confirmed']
		dead = row['Deaths']
		recovered = row['Recovered']
		active = confirmed - dead - recovered
		
		lat, lng = row[lat_col], row[lng_col]
		
		if np.isnan(lat):
			continue
			
		if lat != 0 and lng != 0:
			data_points = add_to_dict(data_points, country, province, admin2, (confirmed, dead, recovered, active, 1, lat, lng))
		else:
			data_points = add_to_dict(data_points, country, province, admin2, (confirmed, dead, recovered, active, 0, 0, 0))

	with web_app.app.app_context():
		for region, stats in data_points.items():
			country, province, admin2 = region
			confirmed, dead, recovered, active, num_regions, lat_sum, lng_sum = stats

			lat = lat_avg = lat_sum/num_regions
			lng = lng_avg = lng_sum/num_regions

			new_data = corona_sql.Datapoint(
				entry_date=entry_date,
				
				admin2=admin2,
				province=province,
				country=country,
				
				latitude=lat,
				longitude=lng,
				
				confirmed=confirmed,
				dead=dead,
				recovered=recovered,
				active=confirmed - recovered - dead
			)

			corona_sql.db.session.add(new_data)
		
		total_confirmed, total_recovered, total_dead, total_active, _, _, _ = data_points[("", "", "")]

		data_entry = corona_sql.DataEntry(
			entry_date=entry_date,
			total_confirmed=total_confirmed,
			total_recovered=total_recovered,
			total_dead=total_dead,
			total_active=total_active
		)
			
		corona_sql.db.session.add(data_entry)
		corona_sql.db.session.commit()
		
		print(f"\tImported data for date {entry_date}")

def download_data_for_date(entry_date):
	date_formatted = entry_date.strftime("%m-%d-%Y")
	
	with web_app.app.app_context():
		existing_data = corona_sql.Datapoint.query.filter(corona_sql.Datapoint.entry_date==entry_date).all()
		if not existing_data:
			print("[DATA IMPORT] Attempting to download " + str(entry_date))
			github_raw_url = f"https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{date_formatted}.csv"
			response = requests.get(github_raw_url)
			
			if response.status_code == 200:
				csv_text = response.text
				import_data(csv_text, entry_date)
				
				print("\tComplete")
				return 'done'
			
			print("\tDate not found")
			return '404'
		
		print("\tEntries already made")
		return 'exists'

# daily reports link: https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports
def data_download():
	time.sleep(5)
	add_date_range(date_1=date(2020, 3, 1), date_2=date.today())
	
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
