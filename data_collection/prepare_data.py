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

    location_data = {"admin0": "", "admin1": "", "admin2": "", **location_data}
    location_data['admin0'], location_data['admin1'], location_data['admin2'] = standards.normalize_name(location_data['admin0'], location_data['admin1'], location_data['admin2'])

    return location_data

def prepare_locations(locations):
    return [prepare_location_data(location_data) for location_data in locations]

def prepare_datapoints(datapoints):
    return [prepare_datapoint_data(datapoint_data) for datapoint_data in datapoints]