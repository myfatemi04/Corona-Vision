from sqlalchemy import create_engine, Column, Integer, Boolean, String, Float, Date
from sqlalchemy.sql import func
from sqlalchemy import and_, between, not_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import json

import os

sql_uri = os.environ['DATABASE_URL']
db = create_engine(sql_uri)
Session = sessionmaker(bind=db)
session = Session()

Base = declarative_base()

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
	is_first_day = Column(Boolean)
	
	confirmed = Column(Integer)
	recovered = Column(Integer)
	dead = Column(Integer)
	active = Column(Integer)
	
	dconfirmed = Column(Integer)
	drecovered = Column(Integer)
	ddead = Column(Integer)
	dactive = Column(Integer)
	
	def json_serializable(self):
		return {
			"data_id": self.data_id,

			"admin2": self.admin2,
			"province": self.province,
			"country": self.country,

			"location_labelled": self.location_labelled,
			"is_first_day": self.is_first_day,

			"latitude": float(self.latitude),
			"longitude": float(self.longitude),

			"confirmed": float(self.confirmed),
			"recovered": float(self.recovered),
			"dead": float(self.dead),
			"active": float(self.active),

			"dconfirmed": float(self.dconfirmed),
			"drecovered": float(self.drecovered),
			"ddead": float(self.ddead),
			"dactive": float(self.dactive)
		}

def total_cases(country, province, date_):
	result = session.query(Datapoint).filter_by(
		country=country,
		province=province,
		admin2='',
		entry_date=date_
	).all()
	
	total_confirmed = 0
	total_recovered = 0
	total_dead = 0
	total_active = 0
	
	for case in result:
		total_confirmed += case.confirmed
		total_recovered += case.recovered
		total_dead += case.dead
		total_active += case.active
		
	return {
		"total_confirmed": total_confirmed,
		"total_recovered": total_recovered,
		"total_dead": total_dead,
		"total_active": total_active
	}

def find_cases_by_location(min_lat, min_lng, max_lat, max_lng):
	lng_condition = between(Datapoint.longitude, min_lng, max_lng)

	if max_lng < min_lng:
		lng_condition = not_(between(Datapoint.longitude, max_lng, min_lng))

	result = session.query(Datapoint).filter(
		and_(
			between(Datapoint.latitude, min_lat, max_lat),
			lng_condition
		)
	)

	return result

def find_cases_by_nation(country='', province='', admin2=''):
	results = session.query(Datapoint)
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