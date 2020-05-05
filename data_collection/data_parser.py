import pandas as pd
import requests
from bs4 import BeautifulSoup
from json_extractor import extract_json_row, json_methods, find_json
from defaults import get_defaults
from datetime import date

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

def import_table(url, table_selector, table_labels, rows=slice(None, None, None)):
	soup = BeautifulSoup(requests.get(url, timeout=10).text, "html.parser")
	df = pd.read_html(get_elem(soup, table_selector).prettify(), keep_default_na=False, na_values=['_'])[0]
	return import_df(df=df, table_labels=table_labels, rows=rows)

def import_df(df, table_labels, rows):
	content = {'datapoint': []}

	defaults = get_defaults()

	for table in table_labels.keys():
		content[table] = []
		labels = {**defaults[table], **table_labels[table]}
		for _, feature in df.iloc[rows].iterrows():
			content[table].append(extract_json_row(feature, labels))
		
	return content

def import_json(url, table_labels, namespace=['features'], allow=[], use_datestr=False):
	if use_datestr:
		url = date.today().strftime(url)
	resp = requests.get(url, timeout=10)

	features = find_json(resp.json(), namespace)
	if type(features) != list:
		features = [features]

	defaults = get_defaults()

	content = {}

	for table in table_labels.keys():
		content[table] = []
		labels = {**defaults[table], **table_labels[table]}
		for feature in features:
			content[table].append(extract_json_row(feature, labels))
	
	return content