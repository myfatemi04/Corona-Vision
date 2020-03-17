import pandas as pd
import corona_sql
import numpy as np
from datetime import date, timedelta
import time
import os
import requests
import web_app

def import_data(datafile):
	dataframe = pd.read_csv(datafile)

	latitude_col = "Lat"
	longitude_col = "Long"
	
	for col in dataframe.columns:
		if 'lat' in col.lower():
			latitude_col = col
		elif 'long' in col.lower():
			longitude_col = col
	
	with web_app.app.app_context():
		results = corona_sql.Datapoint.query.all()
		for result in results:
			corona_sql.db.session.delete(result)
		
		for index, row in dataframe.iterrows():
			lat, lng = row[latitude_col], row[longitude_col]
			confirmed = row['Confirmed']
			dead = row['Deaths']
			recovered = row['Recovered']
			
			
			location_details = []
			if not pd.isnull(row['Province/State']):
				location_details.append(row['Province/State'])
			
			if not pd.isnull(row['Country/Region']):
				location_details.append(row['Country/Region'])
				
			location_string = ", ".join(location_details)
			
			if not np.isnan(lat):
				new_data = corona_sql.Datapoint(location=location_string, latitude=lat, longitude=lng, confirmed=confirmed, dead=dead, recovered=recovered, status=1)
				corona_sql.db.session.add(new_data)
		
		print(f"Imported data from {datafile}")
		corona_sql.db.session.commit()

def download_by_day(date_formatted):
	output_filename = f"./data_downloads/{date_formatted}.csv"
	
	if not os.path.isfile(output_filename):
		print("Attempting download...")
		github_raw_url = f"https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{date_formatted}.csv"
		response = requests.get(github_raw_url)
		
		print(f"Response code: {response.status_code}")
		print(f"Response content length: {len(response.content)}")
		
		if response.status_code == 200:
			csv_content = response.content
			with open(output_filename, "wb") as out:
				out.write(csv_content)
			
			import_data(output_filename)
			
			print("Complete")
			return 'done'
		
		print("Date not found")
		return '404'
	
	print("File already exists")
	return 'exists'

# daily reports link: https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports
def data_download():
	time.sleep(5)
	while True:
		today = date.today()
		today_formatted = today.strftime("%m-%d-%Y")
		
		result = download_by_day(today_formatted)
		
		go_back = timedelta(
			days=-1
		)
		
		latest_day = today
		while result == '404':
			latest_day += go_back
			latest_day_formatted = latest_day.strftime("%m-%d-%Y")
			print("Day not found... trying", latest_day_formatted)
			result = download_by_day(latest_day_formatted)
		
		time.sleep(60)