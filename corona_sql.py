from sqlalchemy import create_engine, Column, Integer, Boolean, String, Float, Date
from sqlalchemy.sql import func
from sqlalchemy import and_, between, not_
from flask_sqlalchemy import SQLAlchemy

import datetime
import json
import os

import standards

sql_uri = os.environ['DATABASE_URL']
db = SQLAlchemy()

Base = db.Model
Integer = db.Integer
Float = db.Float
Boolean = db.Boolean
Date = db.Date
Column = db.Column
String = db.String
DateTime = db.DateTime

class Datapoint(Base):
	__tablename__ = "datapoints"
	data_id = Column(Integer, primary_key=True)
	entry_date = Column(String(16))
	update_time = Column(DateTime, default=datetime.datetime.utcnow())
	
	admin2 = Column(String(320), default='')
	province = Column(String(320), default='')
	country = Column(String(320), default='')
	group = Column(String(320), default='')
	
	latitude = Column(Float(10, 6), default=0)
	longitude = Column(Float(10, 6), default=0)

	location_labelled = Column(Boolean, default=False)
	location_accurate = Column(Boolean, default=False)
	is_first_day = Column(Boolean, default=False)
	is_primary = Column(Boolean, default=False)
	
	confirmed = Column(Integer, default=0)
	recovered = Column(Integer, default=0)
	deaths = Column(Integer, default=0)
	active = Column(Integer, default=0)
	serious = Column(Integer, default=0)
	
	dconfirmed = Column(Integer, default=0)
	drecovered = Column(Integer, default=0)
	ddeaths = Column(Integer, default=0)
	dactive = Column(Integer, default=0)
	dserious = Column(Integer, default=0)

	num_tests = Column(Integer, default=0)

	source_link = Column(String())
	
	def json_serializable(self):
		return {
			"data_id": self.data_id,
			"entry_date": str(self.entry_date),

			"admin2": self.admin2,
			"province": self.province,
			"country": self.country,
			"group": self.group,

			"location_labelled": self.location_labelled,
			"is_first_day": self.is_first_day,

			"latitude": float(self.latitude),
			"longitude": float(self.longitude),

			"confirmed": int(self.confirmed),
			"recovered": int(self.recovered),
			"deaths": int(self.deaths),
			"active": int(self.active),
			"serious": int(self.serious),

			"dconfirmed": int(self.dconfirmed),
			"drecovered": int(self.drecovered),
			"ddeaths": int(self.ddeaths),
			"dactive": int(self.dactive),
			"dserious": int(self.dserious),

			"num_tests": int(self.num_tests),
			"source_link": self.source_link
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

# assume we already have the app context
def add_or_update(session, data, commit=True):
	default_data = {
		'country':'',
		'province':'',
		'admin2':'',
		'group':'',
		'latitude':0,
		'longitude':0,
		'location_labelled':False,
		'location_accurate':False,
		'is_first_day':False,
		'is_primary':False,
		'source_link':'',
		'entry_date':'live'
	}

	# location_labels = {'latitude', 'longitude', 'location_labelled', 'location_accurate'}
	stat_labels = {'confirmed', 'dconfirmed', 'deaths', 'ddeaths', 'serious', 'dserious', 'recovered', 'drecovered', 'active', 'dactive', 'num_tests'}
	for stat in stat_labels:
		default_data[stat] = 0


	for label in default_data:
		if label not in data:
			data[label] = default_data[label]
	for label in data:
		if label not in default_data:
			del data[label]
	
	data['country'] = standards.fix_country_name(data['country'])

	primary = {
		'country': data['country'],
		'province': data['province'],
		'admin2': data['admin2'],
		'entry_date': data['entry_date']
	}

	existing = session.query(Datapoint).filter_by(**primary)
	obj = existing.first()
	if obj:
		json_dict = obj.json_serializable()

		for label in stat_labels:
			if data[label] > json_dict[label]:
				setattr(obj, label, data[label])
				obj.update_time = datetime.datetime.utcnow()
				if data['source_link']:
					obj.source_link = data['source_link']
		
		# now we have an existing object.
		# if the object's location is accurate, we don't
		# touch its location
		if not obj.location_accurate:
			# if the object's location is not accurate, however,
			# we try to estimate its location
			estimated_location_data = standards.get_estimated_location(obj.country, obj.province)
			estimated_location = estimated_location_data['location']
			estimate_accurate = estimated_location_data['accurate']

			# if we could find its location...
			if estimated_location is not None:
				# update the old location
				est_lat, est_lng = estimated_location
				obj.latitude = est_lat
				obj.longitude = est_lng
				obj.location_accurate = estimate_accurate
				obj.location_labelled = True

	else:
		if not data['location_labelled']:
			# if the object's location is not labelled,
			# we try to estimate its location
			estimated_location_data = standards.get_estimated_location(obj.country, obj.province)
			estimated_location = estimated_location_data['location']
			estimate_accurate = estimated_location_data['accurate']

			# if we could find its location...
			if estimated_location is not None:
				# set a location
				est_lat, est_lng = estimated_location
				data['latitude'] = est_lat
				data['longitude'] = est_lng
				data['location_accurate'] = estimate_accurate
				data['location_labelled'] = True

			new_obj = Datapoint(**data)

		session.add(new_obj)
	if commit:
		session.commit()
