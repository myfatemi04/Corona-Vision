import pandas as pd
from corona_sql import *
import numpy as np
from datetime import date, timedelta, datetime
import time
import os
import requests
import web_app
import io
import locations
import json
from bs4 import BeautifulSoup

live_data_sources = json.load(open("data_sources.json"))

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

def import_data(csv_text, entry_date, is_live):
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
		country = fix_country_name(country)
		
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
		i = 0
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

			if i % 500 == 0:
				print("\t" + str(i) + "/" + str(len(data_points)))

			session.add(new_data)

			if admin2 != '' and is_live:
				add_or_update(session,
					admin2=admin2,
					province=province,
					country=country,

					confirmed=confirmed,
					deaths=deaths,
					recovered=recovered,
					active=active,

					dconfirmed=confirmed-yesterday_confirmed,
					ddeaths=deaths-yesterday_deaths,
					drecovered=recovered-yesterday_recovered,
					dactive=active-yesterday_active,

					source_link="https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports",

					commit=False
				)

			i += 1
		
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
			today = date.today()
			yesterday = today + timedelta(days=-1)
			is_live = entry_date >= yesterday
			import_data(csv_text, entry_date, is_live)
			
			print("\tComplete")
			return 'done'
		else:
			print("\tDate not found")
			return '404'

# daily reports link: https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports
def data_download():
	time.sleep(2)
	
	add_date_range(date_1=date(2020, 1, 22), date_2=date.today())
	update_live_data()
	
	while True:
		try:
			status = download_data_for_date(date.today())
			
			update_live_data()
			
			if status == '404' or status == 'exists':
				time.sleep(60)
		except:
			print("There was an exception!")

def update_live_data():
	for datasource in live_data_sources:
		print("Loading new data...")
		args = datasource['args']
		method = methods[datasource['method']]
		# if method in allowed_methods:
		method(**args)

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

BNO_US_CASES = {
	"url": "https://docs.google.com/spreadsheets/u/0/d/e/2PACX-1vR30F8lYP3jG7YOq8es0PBpJIE5yvRVZffOyaqC0GgMBN6yt0Q-NI8pxS7hd1F9dYXnowSC6zpZmW9D/pubhtml/sheet?gid=1902046093&range=A1:I68",
	"default_location": {
		"country": "United States",
		"province": "",
		"admin2": ""
	},
	"location_level": "province",
	"source_url": "https://bnonews.com/index.php/2019/01/tracking-coronavirus-u-s-data/"
}

BNO_WORLD_CASES = {
	"url": "https://docs.google.com/spreadsheets/u/0/d/e/2PACX-1vR30F8lYP3jG7YOq8es0PBpJIE5yvRVZffOyaqC0GgMBN6yt0Q-NI8pxS7hd1F9dYXnowSC6zpZmW9D/pubhtml/sheet?headers=false&gid=0&range=A1:I210",
	"default_location": {
		"country": "",
		"province": "",
		"admin2": ""
	},
	"location_level": "country",
	"source_url": "https://bnonews.com/index.php/2020/04/the-latest-coronavirus-cases/"
}

BNO_CANADA_CASES = {
	"url": "https://docs.google.com/spreadsheets/u/0/d/e/2PACX-1vR30F8lYP3jG7YOq8es0PBpJIE5yvRVZffOyaqC0GgMBN6yt0Q-NI8pxS7hd1F9dYXnowSC6zpZmW9D/pubhtml/sheet?headers=false&gid=338130207&range=A1:I20",
	"default_location": {
		"country": "Canada",
		"province": "",
		"admin2": ""
	},
	"location_level": "province",
	"source_url": "https://bnonews.com/index.php/2020/01/tracking-coronavirus-canada-data/"
}

BNO_AUSTRALIA_CASES = {
	"url": "https://docs.google.com/spreadsheets/u/0/d/e/2PACX-1vR30F8lYP3jG7YOq8es0PBpJIE5yvRVZffOyaqC0GgMBN6yt0Q-NI8pxS7hd1F9dYXnowSC6zpZmW9D/pubhtml/sheet?headers=false&gid=572527899&range=A1:I17",
	"default_location": {
		"country": "Australia",
		"province": "",
		"admin2": ""
	},
	"location_level": "province",
	"source_url": "https://bnonews.com/index.php/2020/01/tracking-coronavirus-australia-data/"
}

BNO_CHINA_CASES = {
	"url": "https://docs.google.com/spreadsheets/u/0/d/e/2PACX-1vR30F8lYP3jG7YOq8es0PBpJIE5yvRVZffOyaqC0GgMBN6yt0Q-NI8pxS7hd1F9dYXnowSC6zpZmW9D/pubhtml/sheet?headers=false&gid=108415730",
	"default_location": {
		"country": "China",
		"province": "",
		"admin2": ""
	},
	"labels": ["location", "confirmed", "deaths", "serious", "", "recovered"],
	"location_level": "province",
	"source_url": "https://bnonews.com/index.php/2019/12/tracking-coronavirus-china-data/"
}

def fix_country_name(country):
	if "china" in country.lower():
		country = "China"  # normalizes "Mainland China"
	if "korea" in country.lower():
		if "south" in country.lower() or "s." in country.lower():
			country = "South Korea"
		elif "republic" in country.lower():
			country = "South Korea"
		elif "north" in country.lower() or "n." in country.lower():
			country = "North Korea"
	
	if country.lower() == "uk":
		country = "United Kingdom"
	elif country.lower() == "us" or country.lower() == "usa":
		country = "United States"
	
	if country.lower() == 'uae':
		country = "United Arab Emirates"

	if country.lower() == 'drc':
		country = "Congo, Democratic Republic of the"

	if country.lower() == 'car':
		country = "Central African Republic"
	
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
	return country

# assume we already have the app context
def add_or_update(session,
				country='',
				province='',
				admin2='',
				confirmed=0,
				dconfirmed=0,
				deaths=0,
				ddeaths=0,
				serious=0,
				dserious=0,
				recovered=0,
				drecovered=0,
				active=0,
				dactive=0,
				num_tests=0,
				source_link='',
				location='',
				group='',
				commit=True):
	country = fix_country_name(country)
	existing = session.query(LiveEntry).filter_by(country=country, province=province, admin2=admin2)
	obj = existing.first()
	if obj:
		updated = False
		if confirmed > obj.confirmed:
			obj.confirmed=confirmed
			updated = True
		if dconfirmed > obj.dconfirmed:
			obj.dconfirmed=dconfirmed
			updated = True
		if deaths > obj.deaths:
			obj.deaths=deaths
			updated = True
		if ddeaths > obj.ddeaths:
			obj.ddeaths=ddeaths
			updated = True
		if serious > obj.serious:
			obj.serious=serious
			updated = True
		if dserious > obj.dserious:
			obj.dserious=dserious
			updated = True
		if recovered > obj.recovered:
			obj.recovered=recovered
			updated = True
		if drecovered > obj.drecovered:
			obj.drecovered=drecovered
			updated = True
		if active > obj.active:
			obj.active=active
			updated = True
		if dactive > obj.dactive:
			obj.dactive=dactive
			updated = True
		if num_tests > obj.num_tests:
			obj.num_tests=num_tests
			updated = True
		if group:
			obj.group=group
			updated = True
		
		if updated:
			obj.update_time = datetime.utcnow()
			if source_link:
				obj.source_link=source_link

	else:
		new_obj = LiveEntry(
			country=country,
			province=province,
			admin2=admin2,
			confirmed=confirmed,
			dconfirmed=dconfirmed,
			deaths=deaths,
			ddeaths=ddeaths,
			serious=serious,
			dserious=dserious,
			recovered=recovered,
			drecovered=drecovered,
			active=active,
			dactive=dactive,
			source_link=source_link,
			num_tests=num_tests
		)

		session.add(new_obj)
	if commit:
		session.commit()

def number(string):
	
	string = string.strip()
	if not string:
		return 0
	string = string.split()[0]
	number = string.replace(",", "").replace("+", "").replace(".", "").replace("*", "")
	try:
		return int(number)
	except:
		return 0

def import_worldometers():
	response = requests.get("http://www.worldometers.info/coronavirus")
	soup = BeautifulSoup(response.text, "html.parser")
	main_countries = soup.find(id="main_table_countries_today")
	labels = ['country', 'confirmed', 'dconfirmed', 'deaths', 'ddeaths', 'recovered', 'active', 'serious', '', '', 'num_tests', '']
	number_labels = {'confirmed', 'dconfirmed', 'deaths', 'ddeaths', 'recovered', 'active', 'serious', 'num_tests'}
	
	data = []
	for row in main_countries.find("tbody").findAll("tr"):
		if row.get("class") and "row_continent" in row.get("class"):
			continue
		tds = row.findAll("td")
		new_data = {"source_link": 'https://www.worldometers.info/coronavirus/'}
		new_data['group'] = "" or tds[-1].get("data-continent")
		for label, td in zip(labels, tds):
			if label:
				if label in number_labels:
					new_data[label] = number(td.text.strip())
				else:
					if label == 'country':
						new_data[label] = fix_country_name(td.text.strip())
						print(new_data[label])
					else:
						new_data[label] = td.text.strip()
		data.append(new_data)

	with web_app.app.app_context():
		session = db.session()
		for row in data:
			if row['country'].lower() in ['overall', 'total', 'world']:
				row['country'] = ''

			row['country'] = fix_country_name(row['country'])
			
			add_or_update(session, **row)

def import_google_sheets(url, default_location, source_url, labels=['province', 'confirmed', 'dconfirmed', 'deaths', 'ddeaths', '', 'serious', 'recovered', '']):
	response = requests.get(url)
	soup = BeautifulSoup(response.text, "html.parser")
	rows = soup.findAll('tr')
	number_labels = {"confirmed", "dconfirmed", "deaths", "ddeaths", "serious", "recovered"}
	data = []

	mode = ""

	for row in rows:
		if "location" in row.text.lower():
			mode = "rows"
		elif mode == "rows":
			tds = row.findAll('td')
			new_data = {**default_location}
			link = row.find('a', href=True)
			if link:
				new_data["source_link"] = link['href']
			else:
				new_data["source_link"] = url

			for label, td in zip(labels, tds):
				if label in number_labels:
					new_data[label] = number(td.text.replace(",", ""))
				else:
					if label:
						new_data[label] = td.text

			data.append(new_data)

	with web_app.app.app_context():
		session = db.session()
		for row in data:
			if row['province'] == 'TOTAL': row['province'] = ''
			if row['country'] == 'TOTAL': row['country'] = ''
			add_or_update(session, **row)
		session.commit()

def import_selector(url, source_link, labels, location):
	try:
		response = requests.get(url)
		soup = BeautifulSoup(response.text, "html.parser")
	except Exception as e:
		print("Error during selector:", e, url)
		return
	
	try:
		data = {**location, "source_link": source_link}
		for label, info in labels.items():
			selectors = info['selectors']
			is_plain = 'type' in info and info['type'] == 'plain'
			text = get_field(soup, selectors)
			
			if not is_plain:
				data[label] = number(text)
			else:
				data[label] = text
	except Exception as e:
		print("Error during selector!", e, location, url)
	
	with web_app.app.app_context():
		session = db.session()
		add_or_update(session, **data)
		session.commit()

def get_elem(soup, selector_chain):
	elem = soup
	for selector in selector_chain:
		elem = elem.select(selector['selector'])
		if 'index' not in selector:
			return elem
		elem = elem[selector['index']]
	
	return elem

def get_field(soup, selector_chain):
	return get_elem(soup, selector_chain).text

def import_csv(url, source_link, location, labels, row='all'):
	try:
		response = requests.get(url)
		df = pd.read_csv(io.StringIO(response.text))
	except Exception as e:
		print("Error during import csv:", e, url)
		return
	
	all_data = []
	if row == 'all':
		for index, row in df.iterrows():
			data = {**location, "source_link": source_link}
			for label in labels:
				data[label] = row[labels[label]]
				
			all_data.append(data)
	else:
		data = {**location, "source_link": source_link}
		row = df.iloc[row]
		for label in labels:
			data[label] = row[labels[label]]
		all_data.append(data)
		
	with web_app.app.app_context():
		session = db.session()
		for data in all_data:
			add_or_update(session, **data)
		session.commit()
	
def import_table(url, source_link, location, table_selector, row_selector, labels):
	try:
		response = requests.get(url)
		soup = BeautifulSoup(response.text, "html.parser")
	except Exception as e:
		print("Error during table:", e, url)
		return
	
	table = get_elem(soup, table_selector)
	rows = get_elem(soup, row_selector)
	all_data = []
	for row in rows:
		try:
			data = {**location, "source_link": source_link}
			for label, info in labels.items():
				selectors = info['selectors']
				is_plain = 'type' in info and info['type'] == 'plain'
				text = get_field(row, selectors)
				
				if not is_plain:
					data[label] = number(text)
				else:
					data[label] = text
			all_data.append(data)
		except Exception as e:
			print("Error during table import!", e, url)

methods = {
	"google_sheets": import_google_sheets,
	"worldometers": import_worldometers,
	"selector": import_selector,
	"csv": import_csv,
	"table": import_table
}

allowed_methods = [import_csv, import_selector]

if __name__ == "__main__":
	# data_download()
	import_worldometers()