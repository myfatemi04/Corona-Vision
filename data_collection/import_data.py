from datetime import date, timedelta, datetime
from bs4 import BeautifulSoup
from corona_sql import Datapoint, Session, upload, update_all_deltas
from flask import Flask, redirect
from threading import Thread
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


data_sources = {'live': [], 'historical': []}
source_files = [
	"data_sources/data_sources.json",
	"data_sources/us_states.json"
]
for filename in source_files:
	data_source = json.load(open(filename, encoding="utf-8"), encoding="utf-8")
	if 'live' in data_source:
		data_sources['live'] += data_source['live']
	if 'historical' in data_source:
		data_sources['historical'] += data_source['historical']

# daily reports link: https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports
def data_download():
	while True:
		try:
			update_live_data()
		except Exception as e:
			print("ERROR DURING DATA COLLECTION: ", e)

def update_live_data():
	for datasource in data_sources['live']:
		print("Loading live data from", datasource['label'])
		upload_datasource(datasource)

def update_historical_data():
	for datasource in data_sources['historical']:
		print("Loading historical data from", datasource['label'])
		upload_datasource(datasource)

def dict_match(source, search):
	for col in search:
		if col in source and source[col] == search[col]:
			return True
	return False

def upload_datasource(datasource):
	try:
		args = datasource['args']
		method = methods[datasource['method']]
		results = method(**args)
		if results:
			if "disallow" in datasource:
				# for each result, go through all the filters and see if they match. if not any of them match, then they're ok.
				results = [result for result in results if not any([dict_match(result, rule) for rule in datasource['disallow']])]

			upload(results, defaults=datasource['defaults'], source_link=datasource['source_link'])
	except Exception as e:
		print("Error during update: ", e, ". Data source: ", datasource['label'])
		traceback.print_tb(sys.exc_info()[2])

def number(string):
	if type(string) == float or type(string) == int:
		return string
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
	labels = ['country', 'total', 'dtotal', 'deaths', 'ddeaths', 'recovered', 'active', 'serious', '', '', 'num_tests', '']
	number_labels = {'total', 'dtotal', 'deaths', 'ddeaths', 'recovered', 'active', 'serious', 'num_tests'}
	
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
	
	return data

def import_google_sheets(url, labels=['province', 'total', 'dtotal', 'deaths', 'ddeaths', '', 'serious', 'recovered', '']):
	response = requests.get(url)
	soup = BeautifulSoup(response.text, "html.parser")
	rows = soup.findAll('tr')
	number_labels = {"total", "dtotal", "deaths", "ddeaths", "serious", "recovered"}
	data = []

	mode = ""

	for row in rows:
		if "links" in row.text.lower() or "mainland china" in row.text.lower():
			mode = "rows"
		elif mode == "rows":
			tds = row.findAll('td')
			new_data = {}

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
			if 'country' in new_data:
				if 'total' in new_data['country'].lower(): new_data['country'] = ''
			data.append(new_data)

	return data

def import_selector(url, labels):
	try:
		response = requests.get(url)
		soup = BeautifulSoup(response.text, "html.parser")
	except Exception as e:
		print("Error during selector:", e, url)
		return
	
	try:
		data = {}
		for label, selectors in labels.items():
			field = get_elem(soup, selectors)
			data[label] = field
	except Exception as e:
		print("Error during selector!", e, url)
		return
	
	return [data]

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

def import_csv(url, labels, row='all'):
	response = requests.get(url)
	df = pd.read_csv(io.StringIO(response.text))
	return import_df(df, labels, row)

def import_table(url, table_selector, labels, row='all'):
	response = requests.get(url)
	soup = BeautifulSoup(response.text, "html.parser")
	table = get_elem(soup, table_selector)
	df = pd.read_html(table.prettify())[0]
	return import_df(df, labels, row)

def import_df(df, labels, row):
	all_data = []
	if row == 'all':
		for _, row in df.iterrows():
			data = {}
			for label in labels:
				label_selector = labels[label]
				if type(label_selector) == list:
					head = row
					for sel in label_selector:
						if sel.startswith("::"):
							head = json_methods[sel](head)
						else:
							head = head[sel]
					data[label] = head
				elif type(label_selector) == str:
					data[label] = row[label_selector]
				
			all_data.append(data)
	else:
		data = {}
		row = df.iloc[row]
		for label in labels:
			data[label] = row[labels[label]]
		all_data.append(data)
		
	return all_data

def import_json(url, labels, namespace, allow=[]):
	resp = requests.get(url)
	content = find_json(resp.json(), namespace)
	data = []
	if type(content) == list:
		for row in content:
			try:
				allowed = True
				for rule in allow:
					select, match, match_type = rule
					if match_type == '==':
						allowed = allowed and (find_json(row, select) == match)
					elif match_type == '!=':
						allowed = allowed and (find_json(row, select) != match)
				if allowed:
					data.append(extract_json_data(row, labels))
			except KeyError:
				print("\rKeyError", end='\r')
	else:
		data.append(extract_json_data(content, labels))
	
	return data
		
def extract_json_data(row, labels):
	result = {}
	for label in labels:
		try:
			j = find_json(row, labels[label])
		except KeyError:
			print("\rKeyError on ", label)
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
	return import_jhu.download_data_for_date(date.today())

def import_jhu_historical():
	return import_jhu.add_date_range(date_1=date(2020, 1, 22), date_2=date.today())

json_methods = {
	"::unixtime": lambda x: datetime.utcfromtimestamp(x//1000).strftime("%Y-%m-%d"),
	"::number": lambda x: number(x),
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
	"update_all_deltas": update_all_deltas,
	"table": import_table
}

bno_countries = [
	'China', 'Canada', 'Australia'
]

app = Flask(__name__)

@app.route("/")
def hello():
	return redirect("https://www.coronavision.us/")

if __name__ == "__main__":
	exit()
	use_server = True

	# DEBUG MARKER
	if len(sys.argv) == 1:
		downloader = Thread(target=data_download, name="Data downloader", daemon=not use_server)
		downloader.start()
	elif sys.argv[1] == 'testlast':
		print("Testing the most recent live data source...")
		upload_datasource(data_sources['live'][-1])
	elif sys.argv[1] == 'historical':
		downloader = Thread(target=update_historical_data, name="Data downloader", daemon=not use_server)
		downloader.start()
	elif sys.argv[1].startswith('jhu'):
		d = sys.argv[1][3:]
		y, m, d = d.split('-')
		y = int(y)
		m = int(m)
		d = int(d)
		import_jhu.download_data_for_date(date(y, m, d))

	if use_server:
		# DEBUG MARKER
		PORT = 6060
		if "PORT" in os.environ:
			PORT = os.environ['PORT']
		app.run("0.0.0.0", port=PORT)
	else:
		input()