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
    from geometry import compress_geo, get_center_long_lat, generate_point_geometry, get_precision

    location_data = {"country": "", "province": "", "county": "", **location_data}
    location_data['country'], location_data['province'], location_data['county'] = standards.normalize_name(location_data['country'], location_data['province'], location_data['county'])
    continent = standards.get_continent(location_data['country'])
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
    return [prepare_location_data(location_data) for location_data in locations if not is_total(location_data['country'])]

def prepare_datapoints(datapoints):
    return [prepare_datapoint_data(datapoint_data) for datapoint_data in datapoints if not is_total(datapoint_data['country'])]