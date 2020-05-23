from corona_sql import Datapoint, Session, try_commit, silent_mode
from datetime import datetime, date, timedelta
from sqlalchemy import func

"""

Recalculating-
Step 1. Find out all locations that need to be recounted (for all dates).
Step 2. Sum up whatever needs to be summed up-- provinces, counties, etc.
Step 3. Update the parent datapoint

"""
def recount(updated, cache):
    from caching import LocationCache
    from corona_sql import Location, try_commit
    
    if not silent_mode:
        print("\rRecounting...", end="\r")

    for country, province, county, entry_date in sorted(updated, reverse=True):
        if not county:
            update_overall(country, province, county, entry_date, cache)

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

def update_overall(country, province, county, entry_date, cache):
    results = cache.session.query(*sums).filter_by(entry_date=entry_date)
    result = filter_children(results, country, province, county).first()

    if any(result):
        cache_data = {"country": country, "province": province, "county": county, "entry_date": entry_date}
        cache_data.update({stat: aggregated for stat, aggregated in zip(stat_labels, result)})
        cache.update_data(cache_data, requireIncreasing=True)