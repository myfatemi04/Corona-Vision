from sqlalchemy import and_, between, not_
from sqlalchemy import create_engine, Column, Integer, Float, Boolean, String, DateTime, Enum, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.sql import func

import os
from datetime import date, datetime, timedelta
import json
import time
import numpy as np

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
		self.admin_level = location_data.get_admin_level(self.admin0, self.admin1, self.admin2)
		
		new_admin0_code, new_admin1_code, new_admin2_code = location_data.get_codes(self.admin0, self.admin1, self.admin2)

		if not self.admin0_code: self.admin0_code = new_admin0_code
		if not self.admin1_code: self.admin1_code = new_admin1_code
		if not self.admin2_code: self.admin2_code = new_admin2_code

		location_data.store_codes(self.admin0, self.admin1, self.admin2, self.admin0_code, self.admin1_code, self.admin2_code)
	
	location_id = Column(Integer, primary_key=True)

	admin0 = Column(String(256))
	admin1 = Column(String(256))
	admin2 = Column(String(256))
	admin0_code = Column(String(2))
	admin1_code = Column(String(2))
	admin2_code = Column(String(10))
	admin_level = Column(Enum('world', 'admin0', 'admin1', 'admin2'))

	latitude = Column(Float(10, 6))
	longitude = Column(Float(10, 6))

	population = Column(Float)
	population_density = Column(Float)
	
	humidity = Column(Float)
	temperature = Column(Float)

	start_cases = Column(Date)
	start_socdist = Column(Date)
	start_lockdown = Column(Date)

	@property
	def location_labelled(self):
		return self.latitude is not None and self.longitude is not None

	@property
	def combined_key(self):
		if self.admin0 == '':
			return "World"
		else:
			combined = self.admin0
			if self.admin1: combined = self.admin1 + ", " + combined
			if self.admin2: combined = self.admin2 + ", " + combined
			return combined

	@property
	def t(self):
		return self.admin0, self.admin1, self.admin2

	#### Generated keys are commented out and replaced with functions ####

	def __str__(self):
		return self.__repr__()

	def __repr__(self):
		if self.latitude and self.longitude:
			return f"<Location {self.combined_key} @{self.latitude:.02f} {self.longitude:.02f}>"
		else:
			return f"<Location {self.combined_key}>"

class Datapoint(Base):
	__tablename__ = "datapoints"

	# columns about the date/time of the datapoint
	entry_date = Column(String(16), primary_key=True)
	update_time = Column(DateTime, default=datetime.utcnow())
	
	# columns about the nominal location
	admin2 = Column(String(320), default='', primary_key=True)
	admin1 = Column(String(320), default='', primary_key=True)
	admin0 = Column(String(320), default='', primary_key=True)
	group = Column(String(320), default='')
	
	# columns about the numeric location
	latitude = Column(Float(10, 6))
	longitude = Column(Float(10, 6))
	
	# determines if this is the first time that that region has been seen
	is_first_day = Column(Boolean, default=False)
	
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

	population = Column(Integer)

	def location_labelled(self):
		return self.latitude != None and self.longitude != None

	def guess_location(self):
		# try to update the location
		if not self.location_labelled():
			# if the object's location is not accurate, however,
			# we try to estimate its location
			estimated_location = standards.get_estimated_location(self.admin0, self.admin1, self.admin2)

			# ^^^ returns none if no accurate data could be found
			if estimated_location:
				# update the old location
				est_lat, est_lng = estimated_location
				self.latitude = est_lat
				self.longitude = est_lng

	def update_data(self, data, source_link, session):
		change = False
		for label in stat_labels:
			if label not in data:
				continue
			my_val = getattr(self, label)
			source_is_calculated = getattr(self, "source_" + label) == "calculated"
			if label in increase_labels:
				if data[label] > my_val or (source_is_calculated and data[label] != my_val):
					# SOURCE IS CALCULATED CHECKER
					# if source_is_calculated:
					# 	print("Updating because the source was 'calculated'")
					setattr(self, label, data[label])
					if label in stat_labels:
						setattr(self, "source_" + label, source_link)
					change = True
			else:
				if data[label] != my_val:
					setattr(self, label, data[label])
					if label in stat_labels:
						setattr(self, "source_" + label, source_link)
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

			if calculated_value != original_value:
				setattr(self, "d" + label, calculated_value)
				self.update_time = datetime.utcnow()

	def location_tuple(self):
		return (self.admin0, self.admin1, self.admin2)

class Hospital(Base):
	__tablename__ = "hospitals"
	hospital_id = Column(Integer, primary_key=True)
	hospital_name = Column(String(256))
	hospital_type = Column(String(256))
	address1 = Column(String(256))
	address2 = Column(String(256))
	admin0 = Column(String(256))
	admin1 = Column(String(256))
	admin2 = Column(String(256))
	licensed_beds = Column(Integer, default=0)
	staffed_beds = Column(Integer, default=0)
	icu_beds = Column(Integer, default=0)
	adult_icu_beds = Column(Integer, default=0)
	pediatric_icu_beds = Column(Integer, default=0)
	potential_beds_increase = Column(Integer, default=0)
	average_ventilator_usage = Column(Integer, default=0)

def add_location_data(new_data, cache, session, add_new=True):
	admin0 = new_data['admin0'] if 'admin0' in new_data else ''
	admin1 = new_data['admin1'] if 'admin1' in new_data else ''
	admin2 = new_data['admin2'] if 'admin2' in new_data else ''

	location_tuple = (admin0, admin1, admin2)
	if location_tuple not in cache['locations']:
		if add_new:
			location = Location(admin0=admin0, admin1=admin1, admin2=admin2)
			session.add(location)
			cache['locations'][location_tuple] = location
		else:
			return None
	else:
		location = cache['locations'][location_tuple]

	for key in new_data:
		if getattr(location, key) != new_data[key]:
			setattr(location, key, new_data[key])
	return location

def get_cache(rows, session):
	if not rows:
		return {}

	# returns locations filtered by the min entry-date, max entry-date
	admin0_seen = set()
	admin1_seen = set()
	admin2_seen = set()

	min_entry_date = None
	max_entry_date = None

	for row in rows:
		if 'admin0' not in row: row['admin0'] = ''
		if 'admin1' not in row: row['admin1'] = ''
		if 'admin2' not in row: row['admin2'] = ''

		admin0_seen.add(row['admin0'])
		admin1_seen.add(row['admin1'])
		admin2_seen.add(row['admin2'])

		entry_date = row['entry_date']

		if min_entry_date is None or entry_date < min_entry_date:
			min_entry_date = entry_date
		if max_entry_date is None or entry_date > max_entry_date:
			max_entry_date = entry_date
	
	# we add a timedelta here to the lower bound so we can reuse this to find daily change
	datapoints = session.query(Datapoint).filter(Datapoint.entry_date.between(min_entry_date - timedelta(days=1), max_entry_date))
	locations = session.query(Location)

	if len(admin0_seen) == 1:
		admin0 = admin0_seen.pop()
		datapoints = datapoints.filter_by(admin0=admin0)
		locations = locations.filter_by(admin0=admin0)
	if len(admin1_seen) == 1:
		admin1 = admin1_seen.pop()
		datapoints = datapoints.filter_by(admin1=admin1)
		locations = locations.filter_by(admin0=admin1)
	if len(admin2_seen) == 1:
		admin2 = admin2_seen.pop()
		datapoints = datapoints.filter_by(admin2=admin2)
		locations = locations.filter_by(admin0=admin2)

	cache = {}
	cache['datapoints'] = {(datapoint.location_tuple(), datapoint.entry_date): datapoint for datapoint in datapoints}
	cache['locations'] = {(location.admin0, location.admin1, location.admin2): location for location in locations}
	return cache

location_labels = ['admin0', 'admin1', 'admin2', 'admin0_code', 'admin1_code', 'admin2_code', 'latitude', 'longitude', 'population']
location_only_labels = ['admin0_code', 'admin1_code', 'admin2_code']
def upload(rows, defaults={}, source_link=''):
	session = Session()
	rows = [_fill_defaults(row, defaults) for row in rows]
	cache = get_cache(rows, session)

	# so we don't have to recount things hella times
	updated = set()

	i = 0
	seen = set()
	for row in rows:
		i += 1
		print(f"Finding changes--{i}/{len(rows)}			   ", end='\r')

		row_link = source_link
		if 'source_link' in row:
			row_link = row['source_link']
			del row['source_link']
		
		# fix the location's name
		row['admin0'], row['admin1'], row['admin2'] = location = standards.normalize_name(row['admin0'], row['admin1'], row['admin2'])
		if (location, row['entry_date']) in seen:
			continue
		else:
			seen.add((location, row['entry_date']))

		row_location_data = {col: row[col] for col in location_labels if col in row}
		add_location_data(row_location_data, cache, session)
		
		# some data is location-specific only
		row = {col: row[col] for col in row if col not in location_only_labels}

		# skip empty datapoints
		has_data = False
		for label in stat_labels:
			if label in row and row[label]:
				has_data = True
		if not has_data:
			continue
		
		# find the already-existing data
		if (location, row['entry_date']) in cache['datapoints']:
			existing = cache['datapoints'][location, row['entry_date']]
			existing.update_data(row, row_link, session)
		else:
			# print("adding new", row['admin0'], row['admin1'], row['admin2'], row['entry_date'])
			existing = Datapoint(**row)
			session.add(existing)
			for label in stat_labels:
				if getattr(existing, label):
					setattr(existing, "source_" + label, row_link)

		existing.guess_location()

		# now we recalculate the totals
		# if was_updated:
		updated.add(((row['admin0'], row['admin1'], row['admin2']), row['entry_date']))
		updated.add(((row['admin0'], row['admin1'],            ''), row['entry_date']))
		updated.add(((row['admin0'],            '',            ''), row['entry_date']))
		updated.add(((''           ,            '',            ''), row['entry_date']))

		# if i % 100 == 0:
		# 	print("\rRecommitting", end='\r')
		# 	session.commit()

	recalculate(updated, session)

	print("Committing all...											   ", end='\r')
	session.commit()
	print("Done committing		 ", end='\r')

def delete_dp(*where):
	print("Here is your input: ", *where)
	print("Is this OK?")
	input("Make sure there's an entry date, and you aren't missing any fields.")
	input("You're 100% sure?")
	print("Deleting")
	
	session = Session()
	results = session.query(Datapoint).filter(*where)
	updates = set()
	for result in results:
		a0, a1, a2 = result.location_tuple()
		updates.add(((a0, a1, a2), result.entry_date))
		updates.add(((a0, a1, ''), result.entry_date))
		updates.add(((a0, '', ''), result.entry_date))
		updates.add((('', '', ''), result.entry_date))
		session.delete(result)

	recalculate(updates, session)
	print("Committing in 10 seconds")
	time.sleep(10)
	session.commit()
	print("Committed")

def recalculate(updated, session):
	i = 0
	unique_days = set()
	for location, entry_date in sorted(updated, reverse=True):
		i += 1
		admin0, admin1, admin2 = location
		if admin2 == '':
			print(f"Recounting {i}/{len(updated)} {location} {entry_date}                           ", end='\r')
			update_overall(admin0, admin1, entry_date, session)
		unique_days.add(entry_date)

	for day in sorted(unique_days):
		# we tell it what was updated so we can skip things that weren't
		update_deltas(day, updated)

def recalculate_selection(*where):
	session = Session()
	results = session.query(Datapoint).filter(*where)
	updates = set()
	for result in results:
		a0, a1, a2 = result.location_tuple()
		updates.add(((a0, a1, a2), result.entry_date))
		updates.add(((a0, a1, ''), result.entry_date))
		updates.add(((a0, '', ''), result.entry_date))
		updates.add((('', '', ''), result.entry_date))
	recalculate(updates, session)
	session.commit()

def _is_nan(data):
	return type(data) == float and np.isnan(data)

def _fill_defaults(data, defaults):
	if 'entry_date' in data:
		if type(data['entry_date']) == str:
			y, m, d = data['entry_date'].split("-")
			data['entry_date'] = date(int(y), int(m), int(d))

	default_data = { 'entry_date': datetime.utcnow().date(), 'group': '', 'admin0': '', 'admin1': '', 'admin2': '', **defaults }

	# add default values if not found
	for label in default_data:
		if label not in data:
			data[label] = default_data[label]
		
	# remove NaN data
	for label in stat_labels:
		if label in data:
			if _is_nan(data[label]):
				del data[label]

	data['admin0'] = standards.fix_admin0_name(data['admin0'])
	data['group'] = standards.get_continent(data['admin0'])

	return data

sums = tuple(func.sum(getattr(Datapoint, label)) for label in stat_labels)

def filter_children(results, admin0, admin1):
	if not admin0: # sum entire world
		results = results.filter(Datapoint.admin0 != '', Datapoint.admin1 == '', Datapoint.admin2 == '')
	elif not admin1: # sum entire country
		results = results.filter(Datapoint.admin0 == admin0, Datapoint.admin1 != '', Datapoint.admin2 == '')
	else: # sum entire state
		results = results.filter(Datapoint.admin0 == admin0, Datapoint.admin1 == admin1, Datapoint.admin2 != '')
	return results

def update_overall(admin0, admin1, entry_date, session):
	results = session.query(*sums).filter_by(entry_date=entry_date)
	results = filter_children(results, admin0, admin1)
	result = results.first()
	if not result or not any(result):
		return
	
	labelled = {x[0]: x[1] for x in zip(stat_labels, result)}
	
	overall_dp = session.query(Datapoint).filter_by(entry_date=entry_date, admin0=admin0, admin1=admin1, admin2='').first()

	if not overall_dp:
		overall_dp = Datapoint(admin0=admin0, admin1=admin1, admin2='', entry_date=entry_date)
		session.add(overall_dp)
		# fill in defaults
		for label in stat_labels:
			setattr(overall_dp, label, 0)
	
	# print(labelled, admin0, admin1, entry_date)
	overall_dp.update_data(labelled, "calculated", session)

def update_deltas(day, updated=None):
	compare_day = day + timedelta(days=-1)
	sess = Session()
	today_datapoints = sess.query(Datapoint).filter_by(entry_date=day)
	yesterday_datapoints = sess.query(Datapoint).filter_by(entry_date=compare_day)

	today_dict = {d.location_tuple(): d for d in today_datapoints}
	yesterday_dict = {d.location_tuple(): d for d in yesterday_datapoints}

	total = len(today_dict)
	i = 0

	for location in today_dict:
		i += 1
		# skip updating datapoints that didn't change
		if (location, day) not in updated and updated is not None:
			print(compare_day, "-->", day, f"{i}/{total} - skip	   ", end='\r')
		else:
			print(compare_day, "-->", day, f"{i}/{total}		   ", end='\r')

		today_dp = today_dict[location]
		active = (float(today_dp.total) - float(today_dp.deaths) - float(today_dp.recovered))
		if today_dp.active != active:
			today_dp.active = active

		if location in yesterday_dict:
			yesterday_dp = yesterday_dict[location]
		else:
			yesterday_dp = None
		
		today_dp.update_differences(yesterday_dp)

	# print("You have to commit deltas manually btw", end="\r")
	# print("Committing deltas...						 ", end='\r')
	# sess.commit()

def update_all_deltas():
	start_date = date(2020, 1, 22)
	end_date = datetime.utcnow().date()
	while start_date <= end_date:
		next_day = start_date + timedelta(days=1)
		update_deltas(start_date, None)
		start_date = next_day

if __name__ == "__main__":
	# delete_dp(Datapoint.admin0 == 'United States', Datapoint.admin1 == 'Recovered')
	# print("Remember to comment this out")
	recalculate_selection(Datapoint.admin0 == "United States", Datapoint.entry_date=='2020-03-05')
	recalculate_selection(Datapoint.admin0 == "United States", Datapoint.entry_date=='2020-03-06')
	recalculate_selection(Datapoint.admin0 == "United States", Datapoint.entry_date=='2020-03-11')