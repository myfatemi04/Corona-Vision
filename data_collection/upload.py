from corona_sql import Session, Datapoint, Location, try_commit
from sqlalchemy import or_, between, func
from datetime import date
from caching import DatapointCache, LocationCache
import prepare_data
import typing
import inspect

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

def upload_datapoints(datapoints: typing.List, verbose: bool = False, force_update: bool = False) -> bool:
    if inspect.isgenerator(datapoints):
        datapoints = list(datapoints)

    if len(datapoints) == 0:
        return

    end = ' ' * 15 + '\r'

    if verbose:
        print("\rStarting upload", end=end)

    session = Session()

    datapoints = prepare_data.prepare_datapoints(datapoints)
    
    cache = DatapointCache.create(datapoints, session)
    cache.force_update = force_update
    cache.update_all(datapoints)

    location_cache = LocationCache.create(datapoints, session)
    
    if verbose:
        print("\rRecounting", end=end)
        
    cache.recount_changes()

    if verbose:
        print("\rCommitting", end=end)

    try_commit(session)

    return cache.was_updated
