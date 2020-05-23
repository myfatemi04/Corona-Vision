from sqlalchemy import func
from corona_sql import Datapoint

"""

Recalculating-
Step 1. Find out all locations that need to be recounted (for all dates).
Step 2. Sum up whatever needs to be summed up-- provinces, counties, etc.
Step 3. Update the parent datapoint

"""
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

def sum_children(country, province, county, entry_date, session):
    results = session.query(*sums).filter_by(entry_date=entry_date)
    result = filter_children(results, country, province, county).first()

    if any(result):
        overall = {"country": country, "province": province, "county": county, "entry_date": entry_date}
        overall.update({stat: aggregated for stat, aggregated in zip(stat_labels, result)})
        return overall
