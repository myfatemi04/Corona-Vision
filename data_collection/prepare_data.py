"""

Data Preparation

"""
def prepare_datapoint_data(datapoint_data):
    import numpy as np
    import standards
    from datetime import datetime

    keys = set(datapoint_data.keys())
    for key in keys:
        if type(datapoint_data[key]) == float and np.isnan(datapoint_data[key]):
            del datapoint_data[key]

    datapoint_data = {"country": "", "province": "", "county": "", "entry_date": datetime.utcnow().date(), **datapoint_data}
    datapoint_data['country'], datapoint_data['province'], datapoint_data['county'] = standards.normalize_name(datapoint_data['country'], datapoint_data['province'], datapoint_data['county'])

    return datapoint_data

def prepare_location_data(location_data):
    import standards

    location_data = {"country": "", "province": "", "county": "", **location_data}
    location_data['country'], location_data['province'], location_data['county'] = standards.normalize_name(location_data['country'], location_data['province'], location_data['county'])
    continent = standards.get_continent(location_data['country'])
    if continent:
        location_data['group'] = continent

    return location_data

def is_total(string):
    return string.lower().startswith("total") or string.lower().endswith("total")

def prepare_locations(locations):
    return [prepare_location_data(location_data) for location_data in locations if not is_total(location_data['country'])]

def prepare_datapoints(datapoints):
    return [prepare_datapoint_data(datapoint_data) for datapoint_data in datapoints if not is_total(datapoint_data['country'])]