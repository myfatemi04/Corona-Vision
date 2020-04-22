from corona_sql import Session, Datapoint, Location, Hospital
from sqlalchemy import or_, between, func
from datetime import date, datetime

def get_location_cache(rows, session):
    if not rows: return {}

    # returns locations filtered by the min entry-date, max entry-date
    country_seen = set()
    province_seen = set()
    county_seen = set()

    for row in rows:
        if type(row) == dict:
            row = {'country': '', 'province': '', 'county': '', **row}
            row_country = row['country']
            row_province = row['province']
            row_county = row['county']
        elif type(row) == tuple:
            row_country = row[0]
            row_province = row[1]
            row_county = row[2]

        country_seen.add(row_country)
        province_seen.add(row_province)
        county_seen.add(row_county)

    locations = session.query(Location)

    if len(country_seen) == 1:
        locations = locations.filter(or_(Location.country==country_seen.pop(), Location.country==''))
    if len(province_seen) == 1:
        locations = locations.filter(or_(Location.province==province_seen.pop(), Location.province==''))
    if len(county_seen) == 1:
        locations = locations.filter(or_(Location.county==county_seen.pop(), Location.county==''))

    return {location.location_tuple(): location for location in locations}

def get_datapoint_cache(rows, session):
    if not rows: return {}

    # returns locations filtered by the min entry-date, max entry-date
    country_seen = set()
    province_seen = set()
    county_seen = set()
    min_entry_date = rows[0]['entry_date']
    max_entry_date = rows[0]['entry_date']
    for row in rows:
        if type(row) == dict:
            row = {'country': '', 'province': '', 'county': '', 'entry_date': datetime.utcnow().date(), **row}
            row_country = row['country']
            row_province = row['province']
            row_county = row['county']
            row_date = row['entry_date']
        elif type(row) == tuple:
            row_country = row[0]
            row_province = row[1]
            row_county = row[2]
            row_date = row[3]
        
        country_seen.add(row_country)
        province_seen.add(row_province)
        county_seen.add(row_county)

        if row_date < min_entry_date:
            min_entry_date = row_date
        if row_date > max_entry_date:
            max_entry_date = row_date

    datapoints = session.query(Datapoint).filter(Datapoint.entry_date.between(min_entry_date, max_entry_date))

    if len(country_seen) == 1:
        datapoints = datapoints.filter(or_(Datapoint.country==country_seen.pop(), Datapoint.country==''))
    if len(province_seen) == 1:
        datapoints = datapoints.filter(or_(Datapoint.province==province_seen.pop(), Datapoint.province==''))
    if len(county_seen) == 1:
        datapoints = datapoints.filter(or_(Datapoint.county==county_seen.pop(), Datapoint.county==''))

    return {datapoint.t: datapoint for datapoint in datapoints}