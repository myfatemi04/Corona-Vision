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
	elif country_code in country_names.values():
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
	elif state_code in state_names.values():
		return state_code

def get_estimated_location(country_name, province_name=''):
	if province_name:
		state_level_location = get_state_location(country_name, state_name)
		if state_level_location:
			return {"location": state_level_location, "accurate": True}

	# if province_name is not empty, it means we failed to find its
	# actual location at this point
	is_accurate = not bool(province_name)
	country_level_location = get_country_location(country_name)
	
	if country_level_location:
		return {"location": country_level_location, "accurate": is_accurate}
	else:
		return {"location": None, "accurate": False}
	

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
	if string.lower().endswith(end):
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

if __name__ == "__main__":
	print("California location: ", get_state_location("US", "California"))
	print("AF code to name: ", get_country_name("AF"))
	print("Afghanistan name to code: ", get_country_code("Afghanistan"))
	print("SD code to location: ", get_country_location("SD"))
	print("Estimated location of Quebec, Canada: ", get_estimated_location("Canada", "Quebec"))
	print("Estimated location of France: ", get_estimated_location("France", ""))
	print("Estimated location of Virginia, US: ", get_estimated_location("United States", "Virginia"))