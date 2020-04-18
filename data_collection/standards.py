import pandas as pd
import numpy as np

state_locations = {}
state_codes = {}
state_names = {}

country_locations = {}
country_codes = {}
country_names = {}
country_continents = {}

country_location_df = pd.read_csv("location_data/country_locations.tsv", sep='\t')
for index, row in country_location_df.iterrows():
	country_code, lat, lng, country_name = row
	country_locations[country_code] = (lat, lng)

country_code_df = pd.read_csv("location_data/country_codes.csv")
for index, row in country_code_df.iterrows():
	code = row['Code']
	name = row['Name']
	country_codes[name.lower()] = code
	country_codes[name.split(",")[0].lower()] = code
	country_names[code] = name

us_state_location_df = pd.read_csv("location_data/us_state_locations.tsv", sep='\t')
for index, row in us_state_location_df.iterrows():
	state_code, lat, lng, state_name = row
	if not pd.isna(lat):
		state_locations['US', state_code] = (lat, lng)
	state_codes['US', state_name.lower()] = state_code
	state_names['US', state_code] = state_name

def get_country_location(country_name):
	country_code = get_country_code(country_name)
	if country_code in country_locations:
		return country_locations[country_code]

def get_country_code(country_name):
	if country_name.lower() in country_codes:
		return country_codes[country_name.lower()]
	elif country_name in country_codes.values():
		return country_name

def get_country_name(country_code):
	if country_code in country_names:
		return country_names[country_code]
	else:
		return country_code

def get_state_location(country_name, state_name):
	country_code = get_country_code(country_name)
	state_code = get_state_code(country_name, state_name)
	if (country_code, state_code) in state_locations:
		return state_locations[country_code, state_code]

def get_state_code(country_name, state_name):
	country_code = get_country_code(country_name)
	state_name = state_name.split(", ")[-1]
	
	if (country_code, state_name.lower()) in state_codes:
		return state_codes[country_code, state_name.lower()]
	elif state_name in state_codes.values():
		return state_name

def get_state_name(country_name, state_code):
	country_code = get_country_code(country_name)
	if (country_code, state_code) in state_names:
		return state_names[country_code, state_code]
	else:
		return state_code

def get_estimated_location(country_name, province_name='', admin2=''):
	# we don't have any admin2 data
	location_possibly_accurate = admin2 == ''

	if province_name:
		state_level_location = get_state_location(country_name, province_name)
		if state_level_location:
			return {"location": state_level_location, "accurate": True and location_possibly_accurate}

	# if province_name is not empty, it means we failed to find its
	# actual location at this point
	is_accurate = not bool(province_name)
	country_level_location = get_country_location(country_name)
	
	if country_level_location:
		return {"location": country_level_location, "accurate": is_accurate and location_possibly_accurate}
	else:
		return {"location": None, "accurate": False and location_possibly_accurate}
	

fixes = {
	"uk": "United Kingdom",
	"us": "United States",
	"usa": "United States",
	"uae": "United Arab Emirates",
	"drc": "Congo, Democratic Republic of the",
	"car": "Central African Republic",
	"viet nam": "Vietnam"
}

in_fixes = {
	("china",): "China",
	("russia",): "Russia",
	("korea", "n."): "North Korea",
	("korea", "s."): "South Korea",
	("korea", "south"): "South Korea",
	("korea", "north"): "North Korea"
}

def remove_start(string, start):
	if string.lower().startswith(start):
		return string[len(start):]
	return string

def remove_end(string, end):
	if string.lower().endswith(end.lower()):
		return string[:-len(end)]
	return string

def fix_country_name(country):
	for req, fix in in_fixes.items():
		should_fix = True
		for part in req:
			if part not in country.lower():
				should_fix = False
		if should_fix:
			country = fix
			break
	
	for fix in fixes:
		if country.lower() == fix:
			country = fixes[fix]
			break

	country = remove_start(country, "the ")
	country = remove_start(country, "republic of")
	country = remove_end(country, ", the")
	country = remove_end(country, " (islamic republic of)")
	
	if country.lower() in ['overall', 'total', 'world']:
		country = ''

	return country

import string
def normalize_name(country, province='', admin2=''):
	if country is None:
		country = ''
	if province is None:
		province = ''
	if admin2 is None:
		admin2 = ''

	country = country.strip()
	province = province.strip()
	admin2 = admin2.strip()

	if country == 'U.S.': country = "United States"
	province = province.replace("U.S.", "US")
	admin2 = admin2.replace("U.S.", "US")

	# country = string.capwords(country)
	# province = string.capwords(province)
	# admin2 = string.capwords(admin2)

	if country == 'Hong Kong SAR':
		country = 'Hong Kong'
	if country == 'Guam':
		country = "United States"
		province = "Guam"
	if country == 'Korea':
		country = 'South Korea'
	if country == "Faeroe Islands":
		country = "Faroe Islands"

	# swap province, admin2
	if province == 'U.S.' and country=='United States':
		province = admin2
		admin2 = ''
	if 'SAR' in country:
		country = country.replace('SAR', '').strip()
	if province == country:
		province = admin2
		admin2 = ''
	if province == get_country_code(country):
		province = admin2
		admin2 = ''

	if 'Virgin Islands' in province and country == 'United States':
		province = 'Virgin Islands'
		country = 'United States'
	
	country = get_country_name(country)
	country = fix_country_name(country)
	if ", " in province and admin2 == '':
		admin2, province = get_admin2_province(country, province)

	province = get_state_name(country, province)
	admin2 = remove_end(admin2, " county")
	if "diamond princess" in province.lower():
		province = "Diamond Princess"
	if "wuhan" in province.lower() and "repatriated" in province.lower():
		province = "Wuhan (repatriated)"
	if province.lower() == 'u.s. virgin islands':
		province = 'Virgin Islands'
	return country, province, admin2

def get_admin2_province(country, province):
	comma_index = province.rfind(", ")
	admin2, state_code = province[:comma_index], province[comma_index + 2:]
	if state_code:
		state_code = state_code.split()[0]
		province = get_state_name(country, state_code) or state_code

		if province == 'D.C.':
			province = "District of Columbia"

	return admin2, province

continent_df = pd.read_csv('location_data/country_continent.csv')
alpha2_to_continent = {}
continent_codes = {
	"EU": "Europe",
	"AS": "Asia",
	"AF": "Africa",
	"OC": "Oceania",
	"NA": "North America",
	"SA": "South America",
	"AN": "Antarctica"
}
for _, row in continent_df.iterrows():
	iso, continent = row
	if pd.isna(continent): continent = 'NA'
	alpha2_to_continent[iso] = continent

def get_continent(country):
	country_code = get_country_code(country)
	if country_code in alpha2_to_continent:
		continent_code = alpha2_to_continent[country_code]
		return continent_codes[continent_code]
	else:
		return ''

if __name__ == "__main__":
	print("California location: ", get_state_location("US", "California"))
	print("AF code to name: ", get_country_name("AF"))
	print("Afghanistan name to code: ", get_country_code("Afghanistan"))
	print("SD code to location: ", get_country_location("SD"))
	print("Estimated location of Quebec, Canada: ", get_estimated_location("Canada", "Quebec"))
	print("Estimated location of France: ", get_estimated_location("France", ""))
	print("Estimated location of Virginia, US: ", get_estimated_location("United States", "Virginia"))
	print("State code of Virginia, US: ", get_state_code("United States", "Virginia"))
	print("Admin2/province of Chicago, IL: ", get_admin2_province("US", "Chicago, IL"))
	print("GU state name: ", get_state_name("US", "GU"))