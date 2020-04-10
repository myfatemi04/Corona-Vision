from datetime import date, timedelta, datetime
from bs4 import BeautifulSoup
from corona_sql import *

import pandas as pd
import numpy as np

import time
import json
import os
import io

import requests
import web_app
import standards
import corona_parser

import import_jhu

live_data_sources = json.load(open("data_sources.json"))

# daily reports link: https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports
def data_download():
	time.sleep(2)
	
	import_jhu.add_date_range(date_1=date(2020, 1, 22), date_2=date.today())
	update_live_data()
	
	while True:
		try:
			status = import_jhu.download_data_for_date(date.today())
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
		try:
			method(**args)
		except Exception as e:
			print("Error during data load!", e, args)

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
	
	with web_app.app.app_context():
		session = db.session()
		for row in main_countries.find("tbody").findAll("tr"):
			if row.get("class") and "row_continent" in row.get("class"):
				continue

			tds = row.findAll("td")
			new_data = {"source_link": 'https://www.worldometers.info/coronavirus/'}
			new_data['group'] = "" or tds[-1].get("data-continent")
			for label, td in zip(labels, tds):
				text = td.text.strip()
				if label:
					if label in number_labels:
						new_data[label] = number(text)
					elif label == 'country':
						new_data[label] = standards.fix_country_name(text)
					else:
						new_data[label] = text

			add_or_update(session, new_data)

def import_google_sheets(url, default_location, labels=['province', 'confirmed', 'dconfirmed', 'deaths', 'ddeaths', '', 'serious', 'recovered', '']):
	response = requests.get(url)
	soup = BeautifulSoup(response.text, "html.parser")
	rows = soup.findAll('tr')
	number_labels = {"confirmed", "dconfirmed", "deaths", "ddeaths", "serious", "recovered"}
	data = []

	mode = ""

	for row in rows:
		if "links" in row.text.lower() or "mainland china" in row.text.lower():
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
						if label == 'province' and td.text:
							new_data[label] = td.text.split("province")[0].strip()

			data.append(new_data)

	with web_app.app.app_context():
		session = db.session()
		for row in data:
			if 'total' in row['province'].lower(): row['province'] = ''
			if 'total' in row['country'].lower(): row['country'] = ''
			add_or_update(session, row)
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
			text = corona_parser.get_field(soup, selectors)
			
			if not is_plain:
				data[label] = number(text)
			else:
				data[label] = text
	except Exception as e:
		print("Error during selector!", e, location, url)
	
	with web_app.app.app_context():
		session = db.session()
		add_or_update(session, data)
		session.commit()

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
			add_or_update(session, data)
		session.commit()

methods = {
	"google_sheets": import_google_sheets,
	"worldometers": import_worldometers,
	"selector": import_selector,
	"csv": import_csv
}

allowed_methods = methods.values() # [import_csv, import_selector]

if __name__ == "__main__":
	# update_live_data()
	# print("Importing from USA")
	# datasource = live_data_sources[0]
	# args = datasource['args']
	# method = methods[datasource['method']]
	# try:
	# 	method(**args)
	# except Exception as e:
	# 	print("Error during data load!", e, args)
	data_download()