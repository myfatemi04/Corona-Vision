from sqlalchemy import and_, between, not_, or_
from sqlalchemy import create_engine, Column, Integer, Float, Boolean, String, DateTime, Enum, Date, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.sql import func

import os
from datetime import date, datetime, timedelta
import json
import time
import numpy as np
from decimal import Decimal

import standards
import location_data

# Keep the actual SQL URL private
sql_uri = os.environ['DATABASE_URL']
engine = create_engine(sql_uri)

# Scoped_session is important here
Session = scoped_session(sessionmaker(bind=engine, autocommit=False))

# Class used to make tables
Base = declarative_base()

stat_labels = ['total', 'deaths', 'recovered', 'serious', 'tests', 'hospitalized']
increase_labels = {'total', 'deaths', 'recovered', 'tests'}

class Location(Base):
	__tablename__ = "locations"

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		# prt("new location-", self.country, self.province, self.county)
		self.admin_level = location_data.get_admin_level(self.country, self.province, self.county)
		
		new_country_code, new_province_code, new_county_code = location_data.get_codes(self.country, self.province, self.county)

		if not self.country_code: self.country_code = new_country_code
		if not self.province_code: self.province_code = new_province_code
		if not self.county_code: self.county_code = new_county_code

		location_data.store_codes(self.country, self.province, self.county, self.country_code, self.province_code, self.county_code)
	
	# location_id = Column(Integer, primary_key=True)

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

	def update(self, new_data):
		for key in ['latitude', 'longitude', 'population', 'population_density', 'humidity', 'temperature']:
			if key in new_data:
				new_value = float(new_data[key] or "0")
				old_value = float(getattr(self, key) or "0")
				if abs(new_value - old_value) > 1e-5:
					setattr(self, key, new_value)
		for key in ['country_code', 'province_code', 'county_code', 'start_cases', 'start_socdist', 'start_lockdown']:
			if key in new_data:
				new_value = new_data[key]
				old_value = getattr(self, key)
				if new_value and not old_value:
					setattr(self, key, new_value)
		if 'geometry' in new_data:
			if not self.geometry:
				self.geometry = new_data['geometry']
				self.geometry_precision = new_data['geometry_precision']
			else:
				old_value = self.geometry
				new_value = new_data['geometry']
				if type(old_value) == str:
					old_value = json.loads(old_value)
				if type(new_value) == str:
					new_value = json.loads(new_value)
				if old_value['type'] != new_value['type']:
					if new_value['type'] != 'Point':
						self.geometry = new_data['geometry']
						self.geometry_precision = new_data['geometry_precision']
				else:
					if new_data['geometry_precision'] > self.geometry_precision:
						# print("updating because of precision")
						self.geometry = new_data['geometry']
						self.geometry_precision = new_data['geometry_precision']

	#### Generated keys are commented out and replaced with functions ####
	@staticmethod
	def add_location_data(new_data, cache=None, session=None, add_new=True):
		import prepare_data
		new_data = prepare_data.prepare_location_data(new_data)
		
		country = new_data['country'] if 'country' in new_data else ''
		province = new_data['province'] if 'province' in new_data else ''
		county = new_data['county'] if 'county' in new_data else ''
		location_tuple = (country, province, county)

		if cache:
			if location_tuple not in cache:
				if add_new:
					location = Location(country=country, province=province, county=county)
					session.add(location)
					cache[location_tuple] = location
				else:
					return None
			location = cache[location_tuple]
		else:
			location = session.query(Location).filter_by(country=country, province=province, county=county).first()
			if location is None:
				if add_new:
					location = Location(country=country, province=province, county=county)
					session.add(location)
				else:
					return None

		location.update(new_data)
		return location


	def __str__(self):
		return self.__repr__()

	def __repr__(self):
		if self.latitude and self.longitude:
			return f"<Location {self.combined_key} @{self.latitude:.02f} {self.longitude:.02f}>"
		else:
			return f"<Location {self.combined_key}>"

class Datapoint(Base):
	__tablename__ = "datapoints"

	def __init__(self, data, source_link):
		super().__init__(**data)
		# prt("new data point-", self.country, self.province, self.province, source_link)
		for label in stat_labels:
			if getattr(self, label) is not None:
				setattr(self, "source_" + label, source_link)

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

	def location_labelled(self):
		return self.latitude != None and self.longitude != None

	def guess_location(self):
		# try to update the location
		if not self.location_labelled():
			# if the object's location is not accurate, however,
			# we try to estimate its location
			estimated_location = standards.get_estimated_location(self.country, self.province, self.county)

			# ^^^ returns none if no accurate data could be found
			if estimated_location:
				# update the old location
				est_lat, est_lng = estimated_location
				self.latitude = est_lat
				self.longitude = est_lng

	def update_data(self, data, source_link):
		change = False
		
		def _update(label, new_val):
			setattr(self, label, new_val)
			if label in stat_labels:
				setattr(self, "source_" + label, source_link)

		for label in stat_labels:
			if label not in data:
				continue
			
			my_val = getattr(self, label)

			if my_val is None:
				_update(label, data[label])
				change = True
			elif label in increase_labels:
				if data[label] > my_val:
					_update(label, data[label])
					change = True
			else:
				if data[label] != my_val:
					_update(label, data[label])
					change = True

		if change:
			self.update_time = datetime.utcnow()

		return change
	
	def update_differences(self, prev_row):
		for label in stat_labels:
			original_value = getattr(self, "d" + label)
			if prev_row is not None:
				calculated_value = getattr(self, label) - getattr(prev_row, label)
			else:
				calculated_value = getattr(self, label)

			if float(calculated_value) != float(original_value):
				setattr(self, "d" + label, calculated_value)
				self.update_time = datetime.utcnow()

	@staticmethod
	def add_datapoint_data(datapoint_data, source_link, session, cache=None):
		import prepare_data
		datapoint_data = prepare_data.prepare_datapoint_data(datapoint_data)
		if cache is not None:
			t = datapoint_data['country'], datapoint_data['province'], datapoint_data['county'], datapoint_data['entry_date'].isoformat()
			if t in cache:
				datapoint = cache[t]
				datapoint.update_data(data=datapoint_data, source_link=source_link)
			else:
				datapoint = Datapoint(data=datapoint_data, source_link=source_link)
				session.add(datapoint)
				cache[datapoint.t] = datapoint
			return datapoint
		else:
			datapoint = session.query(
				country=datapoint_data['country'],
				province=datapoint_data['province'],
				county=datapoint_data['county'],
				entry_date=datapoint_data['entry_date']
			).first()

			if datapoint is not None:
				datapoint.update_data(data=datapoint_data, source_link=source_link)
			else:
				datapoint = Datapoint(data=datapoint_data, source_link=source_link)
				session.add(datapoint)
			return datapoint

	def location_tuple(self):
		return (self.country, self.province, self.county)

	def ripples(self):
		if type(self.entry_date) == str:
			date_str = self.entry_date
		elif type(self.entry_date) == date:
			date_str = self.entry_date.isoformat()
		result = set()
		result.add(('', '', '', date_str))
		result.add((self.country, '', '', date_str))
		result.add((self.country, self.province, '', date_str))
		result.add((self.country, self.province, self.county, date_str))
		return result

	@property
	def t(self):
		return self.country, self.province, self.county, self.entry_date

class Hospital(Base):
	__tablename__ = "hospitals"
	hospital_id = Column(Integer, primary_key=True)
	hospital_name = Column(String(256))
	hospital_type = Column(String(256))
	address1 = Column(String(256))
	address2 = Column(String(256))
	country = Column(String(256))
	province = Column(String(256))
	county = Column(String(256))
	licensed_beds = Column(Integer, default=0)
	staffed_beds = Column(Integer, default=0)
	icu_beds = Column(Integer, default=0)
	adult_icu_beds = Column(Integer, default=0)
	pediatric_icu_beds = Column(Integer, default=0)
	potential_beds_increase = Column(Integer, default=0)
	average_ventilator_usage = Column(Integer, default=0)

