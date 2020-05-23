from sqlalchemy import or_
from sqlalchemy import create_engine, Column, Integer, Float, Boolean, String, DateTime, Enum, Date, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.sql import func

import os
from datetime import date, datetime, timedelta
from decimal import Decimal

silent_mode = False

# Keep the actual SQL URL private
sql_uri = os.environ['DATABASE_URL']
engine = create_engine(sql_uri, encoding='utf-8', pool_pre_ping=True)

# Scoped_session is important here
Session = scoped_session(sessionmaker(bind=engine, autocommit=False))

# Class used to make tables
Base = declarative_base()

stat_labels = ['total', 'deaths', 'recovered', 'serious', 'tests', 'hospitalized']
increase_labels = {'total', 'deaths', 'recovered', 'tests'}

class Location(Base):
	__tablename__ = "locations"

	country = Column(String(256), primary_key=True)
	province = Column(String(256), primary_key=True)
	county = Column(String(256), primary_key=True)

	latitude = Column(Float(10, 6))
	longitude = Column(Float(10, 6))
	
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
		for key in ['latitude', 'longitude']:
			if key in new_data:
				new_value = float(new_data[key] or "0")
				old_value = float(getattr(self, key) or "0")
				if abs(new_value - old_value) > 1e-5:
					setattr(self, key, new_value)

	def __str__(self):
		return self.__repr__()

	def __repr__(self):
		if self.latitude and self.longitude:
			return f"<Location {self.combined_key} @{self.latitude:.02f} {self.longitude:.02f}>"
		else:
			return f"<Location {self.combined_key}>"

class Datapoint(Base):
	__tablename__ = "datapoints"

	def __init__(self, data):
		super().__init__(**data)

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
	serious = Column(Integer, default=0)
	tests = Column(Integer, default=0)
	hospitalized = Column(Integer, default=0)

	def update(self, data, requireIncreasing: bool = False) -> bool:
		change = False
		
		def _update(label, new_val):
			setattr(self, label, new_val)

		for label in stat_labels:
			if label not in data or data[label] is None:
				continue
			
			my_val = getattr(self, label)

			if my_val is None:
				_update(label, data[label])
				change = True
			elif label in increase_labels and requireIncreasing:
				if data[label] > my_val:
					_update(label, data[label])
					change = True
			else:
				if data[label] != my_val and data[label]:
					_update(label, data[label])
					change = True

		if change:
			self.update_time = datetime.utcnow()

		return change

	def location_tuple(self):
		return self.country, self.province, self.county

	def date_str(self):
		if type(self.entry_date) == str:
			return self.entry_date
		elif type(self.entry_date) == date:
			return self.entry_date.isoformat()
		raise ValueError(f"Bad date! {self.entry_date}")

	def parents(self):
		date_str = self.date_str()
		
		if self.country:
			yield ("", "", "", date_str)
		
		if self.province:
			yield (self.country, "", "", date_str)

		if self.county:
			yield (self.country, self.province, "", date_str)

	@property
	def t(self):
		return self.country, self.province, self.county, self.date_str()

	def __str__(self):
		return self.__repr__()
	
	def __repr__(self):
		return f"<Datapoint {self.t}>"

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

def try_commit(sess):
	try:
		sess.commit()
	except:
		sess.rollback()
		raise
	finally:
		sess.close()
