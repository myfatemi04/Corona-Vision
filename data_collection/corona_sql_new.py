from sqlalchemy import create_engine
from sqlalchemy import Boolean, Integer, Date, String, Float, Column, ForeignKey, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import func

import os
from datetime import date, datetime, timedelta

engine = create_engine(os.environ['DATABASE_URL'])

Session = scoped_session(sessionmaker(engine))
Base = declarative_base()

session = Session()

class Datapoint(Base):
    __tablename__ = "test"

    entry_date = Column(Date, primary_key=True)
    update_time = Column(DateTime, default=datetime.utcnow())

    admin0 = Column(String(256), primary_key=True)
    admin1 = Column(String(256), primary_key=True)
    admin2 = Column(String(256), primary_key=True)

    total = Column(Integer)
    deaths = Column(Integer)
    recoveries = Column(Integer)
    # active = Column(Integer)
    tests = Column(Integer)
    serious = Column(Integer)
    hospitalized = Column(Integer)

    total_new = Column(Integer)
    deaths_new = Column(Integer)
    recoveries_new = Column(Integer)
    # active_new = Column(Integer)
    tests_new = Column(Integer)
    serious_new = Column(Integer)
    hospitalized_new = Column(Integer)

    source_total = Column(String())
    source_deaths = Column(String())
    source_recoveries = Column(String())
    source_tests = Column(String())
    source_serious = Column(String())
    source_hospitalized = Column(String())

    def update_differences(self, prev_row):
        for label in stat_labels:
            original_value = getattr(self, label + "_new")
            if prev_row is not None:
                calculated_value = getattr(self, label) - getattr(prev_row, label)
            else:
                calculated_value = getattr(self, label)
            if calculated_value != original_value:
                setattr(self, label + "_new", calculated_value)

    # data can have labels [total, deaths, recoveries, tests, serious, hospitalized]
    def update(self, data, source_link):
        updated = False
        for label in data:
            # if the new data is greater, or the data doesn't exist here yet
            if not getattr(self, label) or data[label] > getattr(self, label):
                updated = True
                self.update_time = datetime.utcnow()
                setattr(self, label, data[label])
                setattr(self, "source_" + label, source_link)

        return updated

    @property
    def t(self):
        return self.entry_date, self.admin0, self.admin1, self.admin2

def get_cache(rows):
    if not rows:
        return {"datapoints": {}, "locations": {}}

    # returns locations filtered by the min entry-date, max entry-date
    admin0_seen = set()
    admin1_seen = set()
    admin2_seen = set()

    min_entry_date = None
    max_entry_date = None

    for entry_date, location, _ in rows:
        if 'admin0' not in location: location['admin0'] = ''
        if 'admin1' not in location: location['admin1'] = ''
        if 'admin2' not in location: location['admin2'] = ''

        admin0_seen.add(location['admin0'])
        admin1_seen.add(location['admin1'])
        admin2_seen.add(location['admin2'])
        if not min_entry_date or entry_date < min_entry_date:
            min_entry_date = entry_date
        if not max_entry_date or entry_date > max_entry_date:
            max_entry_date = entry_date
    
    datapoints = session.query(Datapoint).filter(Datapoint.entry_date.between(min_entry_date, max_entry_date))
    locations = session.query(Location)

    if len(admin0_seen) == 1:
        admin0 = admin0_seen.pop()
        datapoints = datapoints.filter_by(admin0=admin0)
        locations = locations.filter_by(admin0=admin0)
    if len(admin1_seen) == 1:
        admin1 = admin1_seen.pop()
        datapoints = datapoints.filter_by(admin1=admin1)
        locations  = locations.filter_by(admin1=admin1)
    if len(admin2_seen) == 1:
        admin2 = admin2_seen.pop()
        datapoints = datapoints.filter_by(admin2=admin2)
        locations = locations.filter_by(admin2=admin2)
    
    datapoints_cache = {(datapoint.location.t, datapoint.entry_date): datapoint for datapoint in datapoints}
    locations_cache = {location.t: location for location in locations}

    return {"datapoints": datapoints_cache, "locations": locations_cache}

def get_location(cache, location):
    if 'locations' not in cache:
        raise ValueError("'locations' not a key in 'cache' [while adding a location]")

    if 'admin0' not in location: location['admin0'] = ''
    if 'admin1' not in location: location['admin1'] = ''
    if 'admin2' not in location: location['admin2'] = ''
    
    location_tuple = location['admin0'], location['admin1'], location['admin2']

    if location_tuple not in cache['locations']:
        location = Location(**location)
        session.add(location)
        cache['locations'][location_tuple] = location
    return cache['locations'][location_tuple]

def get_datapoint(cache, entry_date, location_tuple):
    if 'datapoints' not in cache:
        raise ValueError("'datapoints' not a key in 'cache' [while adding a datapoint]")

    if (location_tuple, entry_date) not in cache['datapoints']:
        datapoint = Datapoint(entry_date=entry_date, admin0=location_tuple[0], admin1=location_tuple[0], admin2=location_tuple[0])
        session.add(datapoint)
        cache['datapoints'][location_tuple, entry_date] = datapoint
    return cache['datapoints'][location_tuple, entry_date]

def step_1_add(rows, source_link, cache):
    # Rows: (Entry date, {Admin0:..., Admin1:..., Admin2:...}, Data)
    changed_locations = set()

    print("Adding data")

    i = 0
    for entry_date, location, data in rows:
        i += 1
        print(f"{i}/{len(rows)}", end='\r')
        
        if 'admin0' not in location: location['admin0'] = ''
        if 'admin1' not in location: location['admin1'] = ''
        if 'admin2' not in location: location['admin2'] = ''
        
        location_tuple = location['admin0'], location['admin1'], location['admin2']

        datapoint_obj = get_datapoint(cache=cache, entry_date=entry_date, location_tuple=location_tuple)

        if datapoint_obj.update(data=data, source_link=source_link):
            changed_locations.add(((location_tuple[0], location_tuple[1], ''), entry_date))
            changed_locations.add(((location_tuple[0], '', ''), entry_date))
            changed_locations.add((('', '', ''), entry_date))

    return changed_locations

def step_2_recount(updated_locations, source_link, cache):

    print("Recounting locations")

    # Sort them so we recount states before we recount countries
    for location, entry_date in sorted(updated_locations, reverse=True):
        counts = get_count(location, entry_date)
        datapoint_obj = get_datapoint(cache, entry_date, location)
        datapoint_obj.update(counts, "calculated")
        print("Recounting ", location)

def step_3_update_differences(updated_locations):
    unique_dates = set()
    for _, entry_date in updated_locations:
        unique_dates.add(entry_date)

    for entry_date in sorted(unique_dates):
        update_differences(entry_date)

def update_differences(day):
    print(f"Updating differences for {day}", end='\r')

    prev_date = day + timedelta(days=-1)
    today_results = session.query(Datapoint).filter_by(entry_date=day)
    yesterday_results = session.query(Datapoint).filter_by(entry_date=prev_date)
    yesterday_mapped = {result.t: result for result in yesterday_results}

    i = 0
    for today_row in today_results:
        i += 1
        print(f"{i}/{today_results.count()}", end='\r')
        if today_row.t in yesterday_mapped:
            yesterday_row = yesterday_mapped[row.t]
            today_row.update_differences(yesterday_row)
        else:
            today_row.update_differences(None)

def get_count(location, entry_date):
    admin0, admin1, admin2 = location
    results = session.query(Datapoint)
    if not admin0: # it's a worldwide recount
        results = session.query(Datapoint).filter(admin0 != '', admin1 == '')
    elif not admin1: # it's a countrywide recount
        results = session.query(Datapoint).filter(admin0 == admin0, admin1 != '', admin2 == '')
    elif not admin2: # it's a statewide recount
        results = session.query(Datapoint).filter(admin1 == admin1, admin2 != '')
    else:
        raise ValueError(f"Attempting to recount an admin2. {admin0}, {admin1}, {admin2}, {entry_date}")
    return summate(results)

def upload_data(rows, source_link):
    cache = get_cache(rows)
    changed_datapoints = step_1_add(rows, source_link, cache)
    step_2_recount(changed_datapoints, source_link, cache)
    step_3_update_differences(changed_datapoints)
    session.commit()

query = session.query(Location.admin0, Location.admin1, Location.admin2, Location.admin0_code, Location.admin1_code, Location.admin2_code).distinct()
for row in query:
    store_codes(*row)

"""
FORMAT FOR DATA UPLOADS

** Provide a source link **
rows = [
    (entry_date, location, data)
]

location: {
    "admin0": ..., "admin1": ..., "admin2": ...
}

data: {
    total/recoveries/deaths/tests/serious/hospitalized: ...
}

"""

ex_entry_date = date.today()
ex_location = {"admin0": "United States"}
ex_data = {"recoveries": 1000}

example_row = ex_entry_date, ex_location, ex_data
upload_data([example_row], "Testing")