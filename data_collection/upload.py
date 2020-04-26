from corona_sql import Session, Datapoint, Location, Hospital, try_commit
from sqlalchemy import or_, between, func
from datetime import date
import data_caching
import location_data
import prepare_data

"""

DATA UPLOADS

upload(data):
    data = {
        'locations': [],
        'datapoints': [],
        'source_link': "https://.../"
    }

"""
def upload(data):
    import sys
    import traceback
    print("\rUploading content...            ", end='\r')
    datapoints_updated = False
    if data:
        for table, rows in data.items():
            try:
                if table == 'location':
                    upload_locations(rows)
                elif table == 'datapoint':
                    datapoints_updated = upload_datapoints(rows, data['source_link'])
            except Exception as e:
                traceback.print_tb(e.__traceback__)
                sys.stderr.write("Error during {}s upload {} {}".format( table, type(e), e ))
    print("\rDone uploading          ", end='\r')
    return datapoints_updated

def upload_locations(locations):
    print("\rUploading locations", end="\r")
    session = Session()
    locations = prepare_data.prepare_locations(locations)
    cache = data_caching.get_location_cache(locations, session)
    seen = set()
    i = 0
    for location_row in locations:
        i += 1
        t = location_row['country'], location_row['province'], location_row['county']
        if t not in seen:
            seen.add(t)
            Location.add_location_data(location_row, cache, session)
    
    print("\rCommitting locations             ", end='\r')
    try_commit(session)

def upload_datapoints(datapoints, source_link, recount=True):
    import recounting
    if not recount:
        print("Not recounting datapoints")
    print("\rUploading datapoints...             ", end='\r')
    
    session = Session()
    datapoints = prepare_data.prepare_datapoints(datapoints)
    cache = data_caching.get_datapoint_cache(datapoints, session)
    was_updated = False
    updates = set()
    seen = set()
    for datapoint_data in datapoints:
        t = datapoint_data['country'], datapoint_data['province'], datapoint_data['county'], datapoint_data['entry_date'].isoformat()
        if t not in seen:
            seen.add(t)
            updated_datapoint, this_datapoint_updated = Datapoint.add_datapoint_data(datapoint_data=datapoint_data, source_link=source_link, session=session, cache=cache)
            updates.update(updated_datapoint.ripples())
            if this_datapoint_updated:
                was_updated = True
    
    if recount:
        print("\rRecounting             ", end='\r')
        recounting.recount(updates, session=session, source_link=source_link, cache=cache)

    print("\rCommitting             ", end='\r')
    try_commit(session)
    return was_updated
