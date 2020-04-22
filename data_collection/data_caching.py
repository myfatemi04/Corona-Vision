from corona_sql import Session, Datapoint, Location, Hospital
from sqlalchemy import or_, between, func
from datetime import date

def get_location_cache(rows, session):
    if not rows: return {}

    # returns locations filtered by the min entry-date, max entry-date
    admin0_seen = set()
    admin1_seen = set()
    admin2_seen = set()

    for row in rows:
        if type(row) == dict:
            row = {'admin0': '', 'admin1': '', 'admin2': '', **row}
            row_admin0 = row['admin0']
            row_admin1 = row['admin1']
            row_admin2 = row['admin2']
        elif type(row) == tuple:
            row_admin0 = row[0]
            row_admin1 = row[1]
            row_admin2 = row[2]

        admin0_seen.add(row_admin0)
        admin1_seen.add(row_admin1)
        admin2_seen.add(row_admin2)

    locations = session.query(Location)

    if len(admin0_seen) == 1:
        locations = locations.filter(or_(Location.admin0==admin0_seen.pop(), Location.admin0==''))
    if len(admin1_seen) == 1:
        locations = locations.filter(or_(Location.admin1==admin1_seen.pop(), Location.admin1==''))
    if len(admin2_seen) == 1:
        locations = locations.filter(or_(Location.admin2==admin2_seen.pop(), Location.admin2==''))

    return {location.location_tuple(): location for location in locations}

def get_datapoint_cache(rows, session):
    if not rows: return {}

    # returns locations filtered by the min entry-date, max entry-date
    admin0_seen = set()
    admin1_seen = set()
    admin2_seen = set()
    min_entry_date = rows[0]['entry_date']
    max_entry_date = rows[0]['entry_date']
    for row in rows:
        if type(row) == dict:
            row = {'admin0': '', 'admin1': '', 'admin2': '', 'entry_date': datetime.utcnow().date(), **row}
            row_admin0 = row['admin0']
            row_admin1 = row['admin1']
            row_admin2 = row['admin2']
            row_date = row['entry_date']
        elif type(row) == tuple:
            row_admin0 = row[0]
            row_admin1 = row[1]
            row_admin2 = row[2]
            row_date = row[3]
        
        admin0_seen.add(row_admin0)
        admin1_seen.add(row_admin1)
        admin2_seen.add(row_admin2)

        if row_date < min_entry_date:
            min_entry_date = row_date
        if row_date > max_entry_date:
            max_entry_date = row_date

    datapoints = session.query(Datapoint).filter(Datapoint.entry_date.between(min_entry_date, max_entry_date))

    if len(admin0_seen) == 1:
        datapoints = datapoints.filter(or_(Datapoint.admin0==admin0_seen.pop(), Datapoint.admin0==''))
    if len(admin1_seen) == 1:
        datapoints = datapoints.filter(or_(Datapoint.admin1==admin1_seen.pop(), Datapoint.admin1==''))
    if len(admin2_seen) == 1:
        datapoints = datapoints.filter(or_(Datapoint.admin2==admin2_seen.pop(), Datapoint.admin2==''))

    return {datapoint.t: datapoint for datapoint in datapoints}