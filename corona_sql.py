# from sqlalchemy import create_engine, Column, Integer, Boolean, String, Float, Date
# from sqlalchemy.sql import func
# from sqlalchemy import and_, between, not_
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker, scoped_session

# import json

# import os

# sql_uri = os.environ['DATABASE_URL']
# db = create_engine(sql_uri)
# Session = scoped_session(sessionmaker(bind=db))

# Base = declarative_base()

from sqlalchemy import create_engine, Column, Integer, Boolean, String, Float, Date
from sqlalchemy.sql import func
from sqlalchemy import and_, between, not_
from flask_sqlalchemy import SQLAlchemy

import json
import os

sql_uri = os.environ['DATABASE_URL']
db = SQLAlchemy()

Base = db.Model
Integer = db.Integer
Float = db.Float
Boolean = db.Boolean
Date = db.Date
Column = db.Column
String = db.String

class Datapoint(Base):
	__tablename__ = "datapoints"
	data_id = Column(Integer, primary_key=True)
	entry_date = Column(Date)
	
	admin2 = Column(String(320))
	province = Column(String(320))
	country = Column(String(320))
	
	latitude = Column(Float(10, 6))
	longitude = Column(Float(10, 6))

	location_labelled = Column(Boolean)
	location_accurate = Column(Boolean)
	is_first_day = Column(Boolean)
	is_primary = Column(Boolean)
	
	confirmed = Column(Integer)
	recovered = Column(Integer)
	deaths = Column(Integer)
	active = Column(Integer)
	
	dconfirmed = Column(Integer)
	drecovered = Column(Integer)
	ddeaths = Column(Integer)
	dactive = Column(Integer)
	
	def json_serializable(self):
		return {
			"data_id": self.data_id,
			"entry_date": str(self.entry_date),

			"admin2": self.admin2,
			"province": self.province,
			"country": self.country,

			"location_labelled": self.location_labelled,
			"is_first_day": self.is_first_day,

			"latitude": float(self.latitude),
			"longitude": float(self.longitude),

			"confirmed": float(self.confirmed),
			"recovered": float(self.recovered),
			"deaths": float(self.deaths),
			"active": float(self.active),

			"dconfirmed": float(self.dconfirmed),
			"drecovered": float(self.drecovered),
			"ddeaths": float(self.ddeaths),
			"dactive": float(self.dactive)
		}

def total_cases(country, province, date_):
	session = db.session()
	result = session.query(Datapoint).filter_by(
		country=country,
		province=province,
		admin2='',
		entry_date=date_
	).all()
	
	total_confirmed = 0
	total_recovered = 0
	total_deaths = 0
	total_active = 0
	
	for case in result:
		total_confirmed += case.confirmed
		total_recovered += case.recovered
		total_deaths += case.deaths
		total_active += case.active
		
	return {
		"total_confirmed": total_confirmed,
		"total_recovered": total_recovered,
		"total_deaths": total_deaths,
		"total_active": total_active
	}

def find_cases_by_location(min_lat, min_lng, max_lat, max_lng):
	session = db.session()
	results = session.query(Datapoint)
	return filter_by_location(results, min_lat, min_lng, max_lat, max_lng)
	
def filter_by_location(results, min_lat, min_lng, max_lat, max_lng):
	lng_condition = between(Datapoint.longitude, min_lng, max_lng)

	if max_lng < min_lng:
		lng_condition = not_(between(Datapoint.longitude, max_lng, min_lng))

	results = results.filter(
		and_(
			between(Datapoint.latitude, min_lat, max_lat),
			lng_condition
		)
	)

	return results

def find_cases_by_nation(country='', province='', admin2=''):
	session = db.session()
	results = session.query(Datapoint)
	return filter_by_nation(results, country, province, admin2)

def filter_by_nation(results, country, province, admin2):
	if country != 'all':
		results = results.filter_by(
			country=country
		)
	if province != 'all':
		results = results.filter_by(
			province=province
		)
	if admin2 != 'all':
		results = results.filter_by(
			admin2=admin2
		)
	return results

def json_list(cases):
	return json.dumps([case.json_serializable() for case in cases])