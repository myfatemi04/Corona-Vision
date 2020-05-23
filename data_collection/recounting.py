from corona_sql import Datapoint, Session, try_commit, silent_mode
from datetime import datetime, date, timedelta
from sqlalchemy import func

"""

Recalculating-
Step 1. Find out all locations that need to be recounted (for all dates).
Step 2. Sum up whatever needs to be summed up-- provinces, counties, etc.
Step 3. Update the parent datapoint

"""
def recount(updated, session, cache=None):
    from caching import LocationCache
    from corona_sql import Location, try_commit
    
    location_cache = LocationCache.create(updated, session=session)

    if not silent_mode:
        print("\rRecounting...", end="\r")

    for country, province, county, entry_date in sorted(updated, reverse=True):
        if not county:
            location_cache.update_data({
                'country': country,
                'province': province,
                'county': county,
                'entry_date': entry_date
            })
            update_overall(country, province, county, entry_date, session)
    
    try_commit(session)

def filter_children(results, country, province, county):
    if not country:
        # sum entire world
        return results.filter(Datapoint.country != '', Datapoint.province == '', Datapoint.county == '')
    elif not province:
        # sum entire country
        return results.filter(Datapoint.country == country, Datapoint.province != '', Datapoint.county == '')
    else:
        # sum entire state
        return results.filter(Datapoint.country == country, Datapoint.province == province, Datapoint.county != '')

stat_labels = ['total', 'deaths', 'recovered', 'serious', 'tests', 'hospitalized']
sums = [func.sum(getattr(Datapoint, label)) for label in stat_labels]

def update_overall(country, province, county, entry_date, session):
    results = session.query(*sums).filter_by(entry_date=entry_date)
    result = filter_children(results, country, province, county).first()

    if any(result):
        overall_filter = {"country": country, "province": province, "county": "", "entry_date": entry_date}
        overall_dp = session.query(Datapoint).filter_by(**overall_filter).first()

        if not overall_dp:
            overall_dp = Datapoint(overall_filter)
            session.add(overall_dp)
        
        labelled = {stat: aggregated for stat, aggregated in zip(stat_labels, result)}
        
        # always require aggregations to be at or above the original count
        overall_dp.update(labelled, requireIncreasing=True)
