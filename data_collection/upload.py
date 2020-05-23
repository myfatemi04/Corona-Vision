from corona_sql import Session, Datapoint, Location, try_commit
from sqlalchemy import or_, between, func
from datetime import date
from caching import DatapointCache
import prepare_data
import typing

# def upload_locations(locations):
#     if not silent_mode:
#         print("\rUploading locations", end="\r")
#     session = Session()
#     locations = prepare_data.prepare_locations(locations)
#     cache = caching.get_location_cache(locations, session)
#     seen = set()
#     i = 0
#     for location_row in locations:
#         i += 1
#         t = location_row['country'], location_row['province'], location_row['county']
#         if t not in seen:
#             seen.add(t)
#             Location.add_location_data(location_row, cache, session)
    
#     if not silent_mode:
#         print("\rCommitting locations             ", end='\r')
#     try_commit(session)

def upload_datapoints(datapoints: typing.List, verbose: bool = False) -> bool:
    session = Session()

    datapoints = prepare_data.prepare_datapoints(datapoints)
    
    cache = DatapointCache.create(datapoints, session)
    cache.update_all(datapoints)
    
    if verbose:
        print("\rRecounting             ", end='\r')
        
    cache.recount_changes()

    if verbose:
        print("\rCommitting             ", end='\r')

    try_commit(session)

    return cache.was_updated
