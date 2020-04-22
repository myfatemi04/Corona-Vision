from corona_sql import Datapoint, Session
from datetime import datetime, date, timedelta
from sqlalchemy import func

"""

Recalculating-
Step 1. Find out all locations that need to be recounted (for all dates).
Step 2. Sum up whatever needs to be summed up-- provinces, counties, etc.
Step 3. Update the parent datapoint

"""
def recount(updated, source_link, session, cache=None):
    import data_caching
    from corona_sql import Location
    
    i = 0
    unique_days = set()
    location_cache = data_caching.get_location_cache(updated, session=session)

    print("\rRecounting...", end="\r")

    for admin0, admin1, admin2, entry_date in sorted(updated, reverse=True):
        i += 1
        if type(entry_date) == str:
            entry_date = datetime.strptime(entry_date, "%Y-%m-%d").date()

        unique_days.add(entry_date)
        if admin2 == '':
            print(f"Recounting {i}/{len(updated)}", end='\r')#" {(admin0, admin1, admin2)} {entry_date}                              ", end='\r')
            update_overall(admin0, admin1, admin2, entry_date, source_link, session)
            Location.add_location_data({"admin0": admin0, "admin1": admin1, "admin2": admin2}, cache=location_cache, session=session)

    for day in sorted(unique_days):
        # we tell it what was updated so we can skip things that weren't
        update_deltas(day, updated)

def filter_children(results, admin0, admin1, admin2):
    if not admin0: # sum entire world
        results = results.filter(Datapoint.admin0 != '', Datapoint.admin1 == '', Datapoint.admin2 == '')
    elif not admin1: # sum entire country
        results = results.filter(Datapoint.admin0 == admin0, Datapoint.admin1 != '', Datapoint.admin2 == '')
    else: # sum entire state
        results = results.filter(Datapoint.admin0 == admin0, Datapoint.admin1 == admin1, Datapoint.admin2 != '')
    return results

stat_labels = ['total', 'deaths', 'recovered', 'serious', 'tests', 'hospitalized']
sums = tuple(func.sum(getattr(Datapoint, label)) for label in stat_labels)
def update_overall(admin0, admin1, admin2, entry_date, source_link, session):
    results = session.query(*sums).filter_by(entry_date=entry_date)
    results = filter_children(results, admin0, admin1, admin2)
    result = results.first()
    if not result or not any(result):
        return
    
    labelled = {x[0]: x[1] for x in zip(stat_labels, result)}
    _filter = {"admin0": admin0, "admin1": admin1, "admin2": '', "entry_date": entry_date}

    overall_dp = session.query(Datapoint).filter_by(**_filter).first()
    if not overall_dp:
        overall_dp = Datapoint(_filter, source_link)
        session.add(overall_dp)
    
    overall_dp.update_data(labelled, source_link)

def update_deltas(day, updated=None):
    compare_day = day + timedelta(days=-1)
    sess = Session()
    today_datapoints = sess.query(Datapoint).filter_by(entry_date=day)
    yesterday_datapoints = sess.query(Datapoint).filter_by(entry_date=compare_day)

    today_dict = {d.t: d for d in today_datapoints}
    yesterday_dict = {d.location_tuple(): d for d in yesterday_datapoints}

    print("Updating deltas    ", end='\r')

    i = skipped = 0
    for data_tuple, today_dp in today_dict.items():
        i += 1
        # print(f"Updating deltas {i}/{len(today_dict)} {data_tuple}                              ", end='\r')
        # skip updating datapoints that didn't change
        if updated is not None and data_tuple not in updated:
            # print("Skipping delta update", data_tuple, "                       ")
            skipped += 1
            continue

        active = float(today_dp.total) - float(today_dp.deaths) - float(today_dp.recovered)
        if today_dp.active != active:
            today_dp.active = active

        admin0, admin1, admin2, _ = data_tuple
        if (admin0, admin1, admin2) in yesterday_dict:
            yesterday_dp = yesterday_dict[admin0, admin1, admin2]
        else:
            yesterday_dp = None
        
        today_dp.update_differences(yesterday_dp)

    print("Committing deltas", end='\r')

    sess.commit()