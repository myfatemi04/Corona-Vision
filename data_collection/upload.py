from corona_sql import Session, Datapoint, Location, Hospital
from sqlalchemy import or_, between, func
from datetime import date
import data_caching
import location_data
import prepare_data
import traceback

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
    print("\rUploading content...            ", end='\r')
    if data:
        for table, rows in data.items():
            if table == 'location':
                try:
                    upload_locations(rows)
                except Exception as e:
                    print("Error during locations upload", type(e), e)
            elif table == 'datapoint':
                try:
                    upload_datapoints(rows, data['source_link'])
                except Exception as e:
                    print("Error during datapoints upload", type(e), e)
    print("\rDone uploading          ", end='\r')

def upload_locations(locations):
    print("\rUploading locations", end="\r")
    session = Session()
    locations = prepare_data.prepare_locations(locations)
    cache = data_caching.get_location_cache(locations, session)
    seen = set()
    i = 0
    for location_row in locations:
        i += 1
        # print(f"\rUploading locations [{i}/{len(locations)}]          ", end='\r')
        t = location_row['admin0'], location_row['admin1'], location_row['admin2']
        if t in seen:
            pass
            # print("already seen [loc]:", t)
        else:
            seen.add(t)
            Location.add_location_data(location_row, cache, session)
    
    print("\rCommitting locations             ", end='\r')
    session.commit()

def upload_datapoints(datapoints, source_link):
    import recounting
    print("\rUploading datapoints...             ", end='\r')
    
    session = Session()
    datapoints = prepare_data.prepare_datapoints(datapoints)
    cache = data_caching.get_datapoint_cache(datapoints, session)
    updates = set()
    seen = set()
    for datapoint_data in datapoints:
        t = datapoint_data['admin0'], datapoint_data['admin1'], datapoint_data['admin2'], datapoint_data['entry_date'].isoformat()
        if t in seen:
            pass
            # print("already seen [data]:", t)
        else:
            seen.add(t)
            updated_datapoint = Datapoint.add_datapoint_data(datapoint_data=datapoint_data, source_link=source_link, session=session, cache=cache)
            updates.update(updated_datapoint.ripples())
    
    print("\rRecounting             ", end='\r')
    recounting.recount(updates, session=session, source_link=source_link, cache=cache)

    print("\rCommitting             ", end='\r')
    session.commit()
