from datetime import date, timedelta, datetime
from bs4 import BeautifulSoup
from corona_sql import Datapoint, Session, upload, update_all_deltas
import chardet
import json

# data processing
import pandas as pd
import numpy as np

# native python
import traceback
import time
import json
import sys
import os
import io

import requests
import standards
import import_jhu


data_sources = json.load(open("data_sources.json", encoding="utf-8"), encoding="utf-8")

# daily reports link: https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports
def data_download():
	while True:
		try:
			update_live_data()
		except Exception as e:
			print("ERROR DURING DATA COLLECTION: ", e)

def update_live_data():
	# DEBUG MARKER
	for datasource in data_sources['live']:
		try:
			print("Loading live data from", datasource['label'])
			args = datasource['args']
			method = methods[datasource['method']]
			method(**args)
		except Exception as e:
			print("Error during live data update: ", e, ". Data source: ", datasource['label'])
			traceback.print_tb(sys.exc_info()[2])
			

def update_historical_data():
	for datasource in data_sources['historical']:
		try:
			print("Loading historical data from", datasource['label'])
			args = datasource['args']
			method = methods[datasource['method']]
			method(**args)
		except Exception as e:
			print("Error during historical data update: ", e, ". Data source: ", datasource['label'])
			traceback.print_tb(sys.exc_info()[2])

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
		new_data = {}
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
		
		data.append(new_data)
	
	upload(data, source_link="http://www.worldometers.info/coronavirus")

def import_google_sheets(url, defaults, labels=['province', 'confirmed', 'dconfirmed', 'deaths', 'ddeaths', '', 'serious', 'recovered', '']):
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
			new_data = {**defaults}

			for label, td in zip(labels, tds):
				if label in number_labels:
					new_data[label] = number(td.text.replace(",", ""))
				else:
					if label:
						new_data[label] = td.text
						if label == 'province' and td.text:
							new_data[label] = td.text.split("province")[0].strip()

			if 'province' in new_data:
				if 'total' in new_data['province'].lower(): new_data['province'] = ''
			if 'total' in new_data['country'].lower(): new_data['country'] = ''
			data.append(new_data)

	upload(data, defaults, source_link=url)

def import_selector(url, source_link, defaults, labels):
	try:
		response = requests.get(url)
		soup = BeautifulSoup(response.text, "html.parser")
	except Exception as e:
		print("Error during selector:", e, url)
		return
	
	try:
		data = {**defaults}
		for label, selectors in labels.items():
			field = get_elem(soup, selectors)
			data[label] = field
	except Exception as e:
		print("Error during selector!", e, url)
		return
	
	upload([data], source_link=source_link)

def get_elem(soup, selector_chain):
	elem = soup
	for selector in selector_chain:
		if type(selector) == int:
			elem = elem[selector]
		elif type(selector) == str:
			if selector.startswith("::"):
				elem = json_methods[selector](elem)
			else:
				elem = elem.select(selector)
	
	return elem

def import_csv(url, defaults, source_link, labels, row='all'):
	response = requests.get(url)
	df = pd.read_csv(io.StringIO(response.text))
	
	all_data = []
	if row == 'all':
		for _, row in df.iterrows():
			data = {**defaults}
			for label in labels:
				data[label] = row[labels[label]]
				
			all_data.append(data)
	else:
		data = {**defaults}
		row = df.iloc[row]
		for label in labels:
			data[label] = row[labels[label]]
		all_data.append(data)
		
	upload(all_data, defaults, source_link=source_link)

def import_json(url, defaults, source_link, labels, namespace):
	resp = requests.get(url)
	content = find_json(resp.json(), namespace)
	data = []
	if type(content) == list:
		for row in content:
			data.append(extract_json_data(row, defaults, labels))
	else:
		data.append(extract_json_data(content, defaults, labels))
	
	upload(data, defaults, source_link=source_link)
		
def extract_json_data(row, defaults, labels):
	result = {**defaults}
	for label in labels:
		try:
			j = find_json(row, labels[label])
		except KeyError:
			continue
		if j is not None:
			result[label] = j
	return result

def dmy(s):
	d, m, y = s.split("/")
	if len(m) == 1:
		m = "0" + m

	if len(d) == 1:
		d = "0" + d

	return y + "-" + m + "-" + d

def find_json(head, selectors):
	for selector in selectors:
		if selector.startswith("::"):
			head = json_methods[selector](head)
		else:
			head = head[selector]
	return head

def date_t(s):
	return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d")

def import_jhu_runner():
	import_jhu.download_data_for_date(date.today())
	print()

def import_jhu_historical():
	import_jhu.add_date_range(date_1=date(2020, 1, 22), date_2=date.today())

json_methods = {
	"::unixtime": lambda x: datetime.utcfromtimestamp(x//1000).strftime("%Y-%m-%d"),
	"::number": lambda x: number(x.text),
	"::text": lambda x: x.text,
	"::strip": lambda x: x.strip(),
	"::cap": lambda x: x.capitalize(),
	"::dmy": lambda x: datetime.strptime(x, "%d%m%Y").strftime("%Y-%m-%d"),
	"::ymd": lambda x: datetime.strptime(x, "%Y%m%d").strftime("%Y-%m-%d"),
	"::date_t": date_t,
	"::us_state_code": lambda x: standards.get_state_name("United States", x),
	"::str": lambda x: str(x)
}

methods = {
	"google_sheets": import_google_sheets,
	"worldometers": import_worldometers,
	"selector": import_selector,
	"csv": import_csv,
	"json": import_json,
	"jhu": import_jhu_runner,
	"jhu_range": import_jhu_historical,
	"update_all_deltas": update_all_deltas
}

if __name__ == "__main__":
	
	if len(sys.argv) < 2:
		data_download()

	elif sys.argv[1] == 'historical':
		update_historical_data() 