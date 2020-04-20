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

class Datapoint(Base):
	# DEBUG MARKER
	__tablename__ = "datapoints"

	# columns about the date/time of the datapoint
	entry_date = Column(String(16), primary_key=True)
	update_time = Column(DateTime, default=datetime.utcnow())
	
	# columns about the nominal location
	admin2 = Column(String(320), default='', primary_key=True)
	admin1 = Column(String(320), default='', primary_key=True)
	admin0 = Column(String(320), default='', primary_key=True)
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

def time_series(admin0, admin1, admin2):
	session = Session()
	rows = session.query(Datapoint).filter_by(admin0=admin0, admin1=admin1, admin2=admin2).order_by(Datapoint.entry_date).all()
	X = []
	Y = []
	if len(rows) == 0:
		return [], []
	min_date = rows[0].entry_date
	max_date = rows[-1].entry_date
	d = min_date
	i = 0
	while d < max_date:
		X.append(d)
		Y.append(rows[i].total)

		d += timedelta(days=1)
		if i + 1 < len(rows):
			if rows[i + 1].entry_date == d:
				i += 1
	
	return X, Y
