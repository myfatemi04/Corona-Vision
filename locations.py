import pandas as pd
import numpy as np

state_locations = {}
state_codes = {}
state_names = {}

country_locations = {}
country_codes = {}

loc_df = pd.read_csv("location_data/country_locations.tsv", sep='\t')
for index, row in loc_df.iterrows():
    country_code, lat, lng, country_name = row
    country_locations[country_code] = (lat, lng)

code_df = pd.read_csv("location_data/country_codes.csv")
for index, row in code_df.iterrows():
    code = row['Code']
    name = row['Name']
    country_codes[name.lower()] = code
    country_codes[name.split(",")[0].lower()] = code
    state_codes[code] = {}
    state_names[code] = {}
    state_locations[code] = {}

loc_df = pd.read_csv("location_data/us_state_locations.tsv", sep='\t')
for index, row in loc_df.iterrows():
    state_code, lat, lng, state_name = row
    state_locations["US"][state_code] = (lat, lng)
    state_codes["US"][state_name.lower()] = state_code
    state_names["US"][state_code] = state_name

NOT_FOUND = None

def get_country_location(country_name):
    country_code = get_country_code(country_name)
    if not country_code:
        return NOT_FOUND
    elif country_code not in country_locations:
        return NOT_FOUND

    return country_locations[country_code]

def get_location(country_name="United States", state_name=""):
    country_code = get_country_code(country_name)

    if state_name == '':
        return get_country_location(country_name)

    state_code = get_state_code(country_code, state_name)
    if not state_code:
        return NOT_FOUND
        
    return state_locations[country_code][state_code]

def get_country_code(country_name):
    if country_name.lower() in country_codes:
        return country_codes[country_name.lower()]
    elif country_name in country_codes.values():
        return country_name
    else:
        return NOT_FOUND

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
