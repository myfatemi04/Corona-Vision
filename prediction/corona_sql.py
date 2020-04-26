from sqlalchemy import and_, between, not_
from sqlalchemy import create_engine, Column, Integer, Float, Boolean, String, DateTime, Enum, Date, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.sql import func

import os
from datetime import date, datetime, timedelta
import json
import time

# Keep the actual SQL URL private
sql_uri = os.environ['DATABASE_URL']
engine = create_engine(sql_uri)

# Scoped_session is important here
Session = scoped_session(sessionmaker(bind=engine, autocommit=False))

# Class used to make tables
Base = declarative_base()

class Location(Base):
	__tablename__ = "locations"

	country = Column(String(256), primary_key=True)
	province = Column(String(256), primary_key=True)
	county = Column(String(256), primary_key=True)
	country_code = Column(String(2))
	province_code = Column(String(2))
	county_code = Column(String(10))
	admin_level = Column(Enum('world', 'country', 'province', 'county'))

	latitude = Column(Float(10, 6))
	longitude = Column(Float(10, 6))

	population = Column(Float)
	population_density = Column(Float)
	
	humidity = Column(Float)
	temperature = Column(Float)

	start_cases = Column(Date)
	start_socdist = Column(Date)
	start_lockdown = Column(Date)

	geometry = Column(JSON)
	geometry_precision = Column(Integer(), default=6)

	@property
	def location_labelled(self):
		return self.latitude is not None and self.longitude is not None

	@property
	def combined_key(self):
		if self.country == '':
			return "World"
		else:
			combined = self.country
			if self.province: combined = self.province + ", " + combined
			if self.county: combined = self.county + ", " + combined
			return combined

	@property
	def t(self):
		return self.country, self.province, self.county

	def location_tuple(self):
		return self.t

class Datapoint(Base):
	# DEBUG MARKER
	__tablename__ = "datapoints"

	# columns about the date/time of the datapoint
	entry_date = Column(String(16), primary_key=True)
	update_time = Column(DateTime, default=datetime.utcnow())
	
	# columns about the nominal location
	county = Column(String(320), default='', primary_key=True)
	province = Column(String(320), default='', primary_key=True)
	country = Column(String(320), default='', primary_key=True)
	group = Column(String(320), default='')
	
	# COVID-19 stats about this datapoint
	total = Column(Integer, default=0)
	recovered = Column(Integer, default=0)
	deaths = Column(Integer, default=0)
	active = Column(Integer, default=0)
	serious = Column(Integer, default=0)
	tests = Column(Integer, default=0)
	hospitalized = Column(Integer, default=0)
	
	dtotal = Column(Integer, default=0)
	drecovered = Column(Integer, default=0)
	ddeaths = Column(Integer, default=0)
	dactive = Column(Integer, default=0)
	dserious = Column(Integer, default=0)
	dtests = Column(Integer, default=0)
	dhospitalized = Column(Integer, default=0)

	# used mostly for provincial data
	source_total = Column(String())
	source_recovered = Column(String())
	source_deaths = Column(String())
	source_serious = Column(String())
	source_tests = Column(String())
	source_hospitalized = Column(String())

	retail_change = Column(Integer)
	grocery_change = Column(Integer)
	parks_change = Column(Integer)
	transit_change = Column(Integer)
	workplaces_change = Column(Integer)
	residential_change = Column(Integer)

def time_series(country, province, county):
	session = Session()
	rows = session.query(Datapoint).filter_by(country=country, province=province, county=county).order_by(Datapoint.entry_date).all()
	session.close()
	X = []
	Y = []
	if len(rows) == 0:
		return [], []
	min_date = rows[0].entry_date
	max_date = rows[-1].entry_date

	if type(min_date) == str:
		min_date = datetime.strptime(min_date, "%Y-%m-%d").date()
	if type(max_date) == str:
		max_date = datetime.strptime(max_date, "%Y-%m-%d").date()

	d = min_date
	i = 0
	while d < max_date:
		X.append(d)
		Y.append(rows[i].total)

		d += timedelta(days=1)
		if i + 1 < len(rows):
			if rows[i + 1].entry_date == d.isoformat():
				i += 1
	
	return X, Y

def timeSeriesAll(country, province, county):
	session = Session()
	rows = session.query(Datapoint).filter_by(country=country, province=province, county=county).order_by(Datapoint.entry_date).all()
	session.close()
	X = []
	Y = []
	if len(rows) == 0:
		return [], []
	min_date = rows[0].entry_date
	max_date = rows[-1].entry_date

	if type(min_date) == str:
		min_date = datetime.strptime(min_date, "%Y-%m-%d").date()
	if type(max_date) == str:
		max_date = datetime.strptime(max_date, "%Y-%m-%d").date()

	d = min_date
	i = 0
	while d < max_date:
		X.append(d)
		Y.append(rows[i])

		d += timedelta(days=1)
		if i + 1 < len(rows):
			if rows[i + 1].entry_date == d.isoformat():
				i += 1
	
	return X, Y

def getLocationObject(country, province, county):
	session = Session()
	result = session.query(Location).filter_by(country=country, province=province, county=county).first()
	session.close()
	return result