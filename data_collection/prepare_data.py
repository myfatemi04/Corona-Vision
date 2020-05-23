import standards
import re

def number(string):

    if type(string) in [float, int]:
        return string

    if string is None:
        return None

    if type(string) != str:
        raise ValueError(f"Number argument is invalid. type: {type(string)}. value: {string}")

    string = string.strip()
    if len(string) == 0:
        return 0

    string = string.split()[0]
    number = re.sub(r"[,\+\.\*#]", "", string)

    if number.lower() == 'nan':
        return None

    try:
        return int(number)
    except:
        return None

"""

Data Preparation

"""
def prepare_datapoint_data(datapoint_data):
    import numpy as np
    from datetime import datetime, date

    keys = set(datapoint_data.keys())
    for key in keys:
        if type(datapoint_data[key]) == float and np.isnan(datapoint_data[key]):
            del datapoint_data[key]
    
    defaultDate = datetime.utcnow().date()
    datapoint_data = {"country": "", "province": "", "county": "", "entry_date": defaultDate, **datapoint_data}
    datapoint_data['country'], datapoint_data['province'], datapoint_data['county'] = standards.normalize_name(datapoint_data['country'], datapoint_data['province'], datapoint_data['county'])

    for stat in ['total', 'recovered', 'deaths', 'serious', 'hospitalized', 'tests']:
        if stat in datapoint_data:
            datapoint_data[stat] = number(datapoint_data[stat])

    return datapoint_data

def prepare_location_data(location_data):
    location_data = {"country": "", "province": "", "county": "", **location_data}
    location_data['country'], location_data['province'], location_data['county'] = standards.normalize_name(location_data['country'], location_data['province'], location_data['county'])
    country_code = standards.country_codes_reverse.get(location_data['country'], '')
    continent = standards.alpha2_to_continent.get(country_code, '')
    if continent:
        location_data['group'] = continent

    return location_data

def is_total(string):
    return string.lower().startswith("total") or string.lower().endswith("total")

def prepare_locations(locations):
    return [prepare_location_data(location_data) for location_data in locations if not is_total(location_data['country'])]

def prepare_datapoints(datapoints):
    return [prepare_datapoint_data(datapoint_data) for datapoint_data in datapoints if not is_total(datapoint_data['country'])]