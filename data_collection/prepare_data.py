"""

Data Preparation

"""
def prepare_datapoint_data(datapoint_data):
    import numpy as np
    import standards
    from datetime import date

    keys = set(datapoint_data.keys())
    for key in keys:
        if type(datapoint_data[key]) == float and np.isnan(datapoint_data[key]):
            del datapoint_data[key]

    datapoint_data = {"admin0": "", "admin1": "", "admin2": "", "entry_date": date.today(), **datapoint_data}
    datapoint_data['admin0'], datapoint_data['admin1'], datapoint_data['admin2'] = standards.normalize_name(datapoint_data['admin0'], datapoint_data['admin1'], datapoint_data['admin2'])

    return datapoint_data

def prepare_location_data(location_data):
    import standards
    from geometry import compress_geo, get_center_long_lat, generate_point_geometry, get_precision

    location_data = {"admin0": "", "admin1": "", "admin2": "", **location_data}
    location_data['admin0'], location_data['admin1'], location_data['admin2'] = standards.normalize_name(location_data['admin0'], location_data['admin1'], location_data['admin2'])
    continent = standards.get_continent(location_data['admin0'])
    if continent:
        location_data['group'] = continent

    if 'geometry' in location_data and location_data['geometry']:
        location_data['geometry'] = compress_geo(location_data['geometry'])
        if 'latitude' not in location_data and 'longitude' not in location_data:
            location_data['longitude'], location_data['latitude'] = get_center_long_lat(location_data['geometry'])
    else:
        if 'latitude' in location_data and 'longitude' in location_data:
            location_data['geometry'] = generate_point_geometry(lng=location_data['longitude'], lat=location_data['latitude'])
            location_data['geometry_precision'] = get_precision(location_data['longitude'], location_data['latitude'])

    return location_data

def is_total(string):
    return string.lower().startswith("total") or string.lower().endswith("total")

def prepare_locations(locations):
    return [prepare_location_data(location_data) for location_data in locations if not is_total(location_data['admin0'])]

def prepare_datapoints(datapoints):
    return [prepare_datapoint_data(datapoint_data) for datapoint_data in datapoints if not is_total(datapoint_data['admin0'])]