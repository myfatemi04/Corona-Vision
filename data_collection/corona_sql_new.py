from sqlalchemy import create_engine
from sqlalchemy import Boolean, Integer, Date, String, Float, Column, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

import os

engine = create_engine(os.environ['DATABASE_URL'])

Session = scoped_session(sessionmaker(engine))
Base = declarative_base()

class Location(Base):
    __tablename__ = "locations"
    location_id = Column(Integer, primary_key=True)
    admin0 = Column(String(256))
    admin1 = Column(String(256))
    admin2 = Column(String(256))
    admin0_code = Column(String(2))
    admin1_code = Column(String(2))

    latitude = Column(Float(10, 6))
    longitude = Column(Float(10, 6))

    population = Column(Float)
    area = Column(Float)
    # population_density = Column(Float)

    # location_labelled = Column(Boolean)
    @property
    def location_labelled(self):
        return self.latitude is not None and self.longitude is not None

    @property
    def population_density(self):
        return float(self.population / self.area)

    @property
    def combined_key(self):
        if self.admin0 == '':
            return "World"
        else:
            combined = self.admin0
            if self.admin1: combined = self.admin1 + ", " + combined
            if self.admin2: combined = self.admin2 + ", " + combined
            return combined

    #### Generated keys are commented out and replaced with functions ####

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        if self.latitude and self.longitude:
            return f"<Location {self.combined_key} @{self.latitude:.02f} {self.longitude:.02f}>"
        else:
            return f"<Location {self.combined_key}>"

class Datapoint(Base):
    __tablename__ = "test"

    entry_date = Column(Date, primary_key=True)
    location_id = Column(Integer, ForeignKey("locations.location_id"), primary_key=True)

    total = Column(Integer, default=0)
    deaths = Column(Integer, default=0)
    recoveries = Column(Integer, default=0)
    # active = Column(Integer)

    total_new = Column(Integer, default=0)
    deaths_new = Column(Integer, default=0)
    recoveries_new = Column(Integer, default=0)
    # active_new = Column(Integer)

def add_location_data(new_data, session):
    admin0 = new_data['admin0'] if 'admin0' in new_data else ''
    admin1 = new_data['admin1'] if 'admin1' in new_data else ''
    admin2 = new_data['admin2'] if 'admin2' in new_data else ''

    location = session.query(Location).filter_by(admin0=admin0, admin1=admin1, admin2=admin2).first()
    if not location:
        location = Location(admin0=admin0, admin1=admin1, admin2=admin2)
        session.add(location)
    for key in new_data:
        setattr(location, key, new_data[key])

session = Session()

import pandas as pd
import json

# country_location_df = pd.read_csv("location_data/country_locations.tsv", sep='\t', keep_default_na=False, na_values=['_'])
# for index, row in country_location_df.iterrows():
#     country_code, lat, lng, country_name = row
#     country = {}
#     country['latitude'] = lat
#     country['longitude'] = lng
#     country['admin0_code'] = country_code
#     country['admin0'] = country_name
#     add_location_data(country, session)

# state_location_df = pd.read_csv("location_data/us_state_locations.tsv", sep='\t', keep_default_na=False, na_values=['_'])
# for _, row in state_location_df.iterrows():
#     state_code, lat, lng, state_name = row
#     state = {}
#     state['latitude'] = lat or None
#     state['longitude'] = lng or None
#     state['admin1_code'] = state_code
#     state['admin1'] = state_name
#     state['admin0'] = 'United States'
#     state['admin0_code'] = 'US'
#     add_location_data(state, session)

us_counties = pd.read_csv("location_data/county_locations.txt", sep='|')
print(len(us_counties))

# session.commit()

# for location in session.query(Location):
#     print(location)