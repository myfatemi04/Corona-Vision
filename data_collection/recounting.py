from corona_sql import Datapoint, Session, try_commit
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

    for country, province, county, entry_date in sorted(updated, reverse=True):
        i += 1
        if type(entry_date) == str:
            entry_date = datetime.strptime(entry_date, "%Y-%m-%d").date()

        unique_days.add(entry_date)
        if county == '':
            # print(f"Recounting {i}/{len(updated)}", end='\r')#" {(country, province, county)} {entry_date}                              ", end='\r')
            update_overall(country, province, county, entry_date, source_link, session)
            Location.add_location_data({"country": country, "province": province, "county": county}, cache=location_cache, session=session)

    # we no longer need to update daily changes; we do it on-the-fly instead
    # for day in sorted(unique_days):
    #     # we tell it what was updated so we can skip things that weren't
    #     update_deltas(day, updated)

def filter_children(results, country, province, county):
    if not country: # sum entire world
        results = results.filter(Datapoint.country != '', Datapoint.province == '', Datapoint.county == '')
    elif not province: # sum entire country
        results = results.filter(Datapoint.country == country, Datapoint.province != '', Datapoint.county == '')
    else: # sum entire state
        results = results.filter(Datapoint.country == country, Datapoint.province == province, Datapoint.county != '')
    return results

stat_labels = ['total', 'deaths', 'recovered', 'serious', 'tests', 'hospitalized']
sums = tuple(func.sum(getattr(Datapoint, label)) for label in stat_labels)
def update_overall(country, province, county, entry_date, source_link, session):
    results = session.query(*sums).filter_by(entry_date=entry_date)
    results = filter_children(results, country, province, county)
    result = results.first()
    if not result or not any(result):
        return
    
    labelled = {x[0]: x[1] for x in zip(stat_labels, result)}
    _filter = {"country": country, "province": province, "county": '', "entry_date": entry_date}

    overall_dp = session.query(Datapoint).filter_by(**_filter).first()
    if not overall_dp:
        overall_dp = Datapoint(_filter, source_link)
        session.add(overall_dp)
    
    overall_dp.update_data(labelled, source_link, requireIncreasing=True)

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

        country, province, county, _ = data_tuple
        if (country, province, county) in yesterday_dict:
            most_recent_dp = yesterday_dict[country, province, county]
        else:
            most_recent_date = sess.query(func.max(Datapoint.entry_date))\
                .filter(Datapoint.entry_date < day)\
                .filter_by(country=country, province=province, county=county)\
                .first()
            if most_recent_date:
                most_recent_dp = sess.query(Datapoint).filter_by(
                    entry_date=most_recent_date,
                    country=country,
                    province=province,
                    county=county
                ).first()
            else:
                most_recent_dp = None
        
        today_dp.update_differences(most_recent_dp)

    print("Committing deltas", end='\r')
    try_commit(sess)