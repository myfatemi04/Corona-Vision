import pandas as pd
import corona_sql
import numpy as np
from datetime import date, timedelta
import time
import os
import requests
import web_app
import io

def import_data(csv_text, entry_date):
	string_io = io.StringIO(csv_text)
	dataframe = pd.read_csv(string_io)
	
	if 'Latitude' not in dataframe.columns:
		print("\tNo latitude or longitude data")
		return
	
	with web_app.app.app_context():
		total_confirmed = 0
		total_recovered = 0
		total_dead = 0
		
		for index, row in dataframe.iterrows():
			lat, lng = row['Latitude'], row['Longitude']
			
			confirmed = row['Confirmed']
			dead = row['Deaths']
			recovered = row['Recovered']
			
			total_confirmed += confirmed
			total_recovered += recovered
			total_dead += dead
			
			location_details = []
			if not pd.isnull(row['Province/State']):
				location_details.append(row['Province/State'])
			
			if not pd.isnull(row['Country/Region']):
				location_details.append(row['Country/Region'])
				
			location_string = ", ".join(location_details)
			
			if not np.isnan(lat):
				new_data = corona_sql.Datapoint(
					entry_date=entry_date,
					location=location_string,
					latitude=lat,
					longitude=lng,
					confirmed=confirmed,
					dead=dead,
					recovered=recovered,
					status=1
				)
				corona_sql.db.session.add(new_data)
			
		data_entry = corona_sql.DataEntry(
			entry_date=entry_date,
			total_confirmed=total_confirmed,
			total_recovered=total_recovered,
			total_dead=total_dead
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
			
			print(f"\tResponse code: {response.status_code}")
			print(f"\tResponse content length: {len(response.text)}")
			
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
	# add_date_range(date_1=date(2020, 1, 22), date_2=date.today())
	# return
	
	while True:
		today = date.today()
		today_formatted = today.strftime("%m-%d-%Y")
		result = download_data_for_date(today)
		
		latest_day = today
		go_back = timedelta(days=-1)
		while result == '404':
			latest_day += go_back
			latest_day_formatted = latest_day.strftime("%m-%d-%Y")
			print("\tTrying", latest_day_formatted)
			result = download_data_for_date(latest_day)
		
		time.sleep(60)
	

""" Should only be used when first setting up the app"""	
def add_date_range(date_1, date_2):
	next_date = timedelta(days=1)
	current_date = date_1
	while current_date <= date_2:
		download_data_for_date(current_date)
		current_date += next_date
