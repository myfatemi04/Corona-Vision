import pandas as pd
import numpy as np
import json

def switch_keys(myDict):
	return {value: key for key, value in myDict.items()}

state_codes = {}
state_codes['United States'] = json.load(open("./location_data/state_codes_us.json"))
state_codes['China'] = json.load(open("./location_data/cn_province_names.json", encoding="utf-8"))

country_codes = json.load(open("./location_data/country_codes.json"))
country_codes_reverse = switch_keys(country_codes)
alpha2_to_continent = json.load(open("./location_data/continents.json"))

aliases = json.load(open("./location_data/aliases.json"))

def remove_start(string, start):
	if string.lower().startswith(start):
		return string[len(start):]
	return string

def remove_end(string, end):
	if string.lower().endswith(end.lower()):
		return string[:-len(end)]
	return string

import string
import re
def normalize_name(country: str, province: str = '', county: str = ''):
	country = country.strip()
	province = province.strip()
	county = county.strip()

	if country in country_codes:
		country = country_codes[country]

	if country in state_codes:
		if province in state_codes[country]:
			province = state_codes[country][province]

	if ", " in province and county == '':
		county, province_id = province.split(", ")

	for regex, actual in aliases['country'].items():
		country = re.sub(regex, actual, country, flags=re.IGNORECASE)

	for regex, actual in aliases['province'].items():
		province = re.sub(regex, actual, province, flags=re.IGNORECASE)
	
	for regex, actual in aliases['county'].items():
		county = re.sub(regex, actual, county, flags=re.IGNORECASE)

	# idk why this would happen but just to be safe
	county = county.replace("U.S.", "US")

	# guam will be listed under the US
	if 'Guam' in country:
		country = 'United States'
		province = 'Guam'

	# remove "district of columbia, district of columbia, us" case
	if country == 'United States' and province.lower() == "district of columbia":
		county = ''

	if province.lower() == 'u.s. virgin islands':
		country = 'United States'
		province = 'Virgin Islands'
	
	return country, province, county

continent_codes = {
	"EU": "Europe",
	"AS": "Asia",
	"AF": "Africa",
	"OC": "Oceania",
	"NA": "North America",
	"SA": "South America",
	"AN": "Antarctica"
}

if __name__ == "__main__":
	print(normalize_name("US", "NY", "New York City"))
	print(normalize_name("US", "NY", "Orange County"))