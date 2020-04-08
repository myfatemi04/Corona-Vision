import pandas as pd
import numpy as np
import json

state_locations = {}
state_codes = {}
state_names = {}

countries = json.load(open("location_data/Country_Locations.json"))['ref_country_codes']
country_dict = {country['numeric']: country for country in countries}

population_df = pd.read_csv("location_data/Population_Data.csv")
for index, row in population_df.iterrows():
    if row['Time'] == 2020:
        country_dict[row['LocID']]['PopTotal'] = row['PopTotal']
        country_dict[row['LocID']]['PopDensity'] = row['PopDensity']

print("Loaded population data")

loc_df = pd.read_csv("location_data/us_state_locations.tsv", sep='\t')
for index, row in loc_df.iterrows():
    state_code, lat, lng, state_name = row
    state_locations["US"][state_code] = (lat, lng)
    state_codes["US"][state_name.lower()] = state_code
    state_names["US"][state_code] = state_name
print("Loaded state locations")

NOT_FOUND = None

def get_location(country_name="United States", state_name=""):
    country_code = get_country_code(country_name)

    if state_name == '':
        return get_country_location(country_name)

    state_code = get_state_code(country_code, state_name)
    if not state_code:
        return NOT_FOUND
        
    return state_locations[country_code][state_code]

def get_state_code(country_code, state_name):
    if country_code not in state_codes:
        return NOT_FOUND

    state_name = state_name.split(", ")[-1]
    
    if state_name.lower() in state_codes[country_code]:
        return state_codes[country_code][state_name.lower()]
    elif state_name in state_codes[country_code].values():
        return state_name
    else:
        return NOT_FOUND

def get_state_name(country_code, state_code):
    if country_code in state_names:
        if state_code in state_names[country_code]:
            return state_names[country_code][state_code]
        elif state_code in state_names[country_code].values():
            return state_code
    
    return None
