from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy import and_, between

db = SQLAlchemy()

class DataEntry(db.Model):
	__tablename__ = "data_entries"
	entry_date = db.Column(db.Date, primary_key=True)
	total_confirmed = db.Column(db.Integer)
	total_recovered = db.Column(db.Integer)
	total_dead = db.Column(db.Integer)
	total_active = db.Column(db.Integer)

class Datapoint(db.Model):
	__tablename__ = "datapoints"
	data_id = db.Column(db.Integer, primary_key=True)
	entry_date = db.Column(db.Date)
	
	province = db.Column(db.String(320))
	country = db.Column(db.String(320))
	
	latitude = db.Column(db.Float(10, 6))
	longitude = db.Column(db.Float(10, 6))
	
	confirmed = db.Column(db.Integer)
	recovered = db.Column(db.Integer)
	dead = db.Column(db.Integer)
	active = db.Column(db.Integer)
	
	def json_serializable(self):
		return {
			"data_id": self.data_id,
			"province": self.province,
			"country": self.country,
			"latitude": float(self.latitude),
			"longitude": float(self.longitude),
			"confirmed": float(self.confirmed),
			"recovered": float(self.recovered),
			"dead": float(self.dead),
			"active": float(self.active)
		}

class User(db.Model):
	__tablename__ = "users"
	user_id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(320))
	firstname = db.Column(db.String(32))
	lastname = db.Column(db.String(32))
	password_encrypt = db.Column(db.String(256))

def find_country_total(country, date_):
	result = Datapoint.query.filter(
		and_(
			Datapoint.country == country,
			Datapoint.entry_date == date_
		)
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

def find_cases(ne_lat, ne_lng, sw_lat, sw_lng, entry_date):
	min_lat = sw_lat
	max_lat = ne_lat
	
	min_lng = sw_lng
	max_lng = ne_lng
	
	result = Datapoint.query.filter(
		and_(
			between(Datapoint.latitude, min_lat, max_lat),
			between(Datapoint.longitude, min_lng, max_lng),
			Datapoint.entry_date==entry_date
		)
	)
	return result.all()
