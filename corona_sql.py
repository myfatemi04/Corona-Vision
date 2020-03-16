from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy import and_

db = SQLAlchemy()

class Datapoint(db.Model):
	__tablename__ = "datapoints"
	data_id = db.Column(db.Integer, primary_key=True)
	location = db.Column(db.String(320))
	latitude = db.Column(db.Float(10, 6))
	longitude = db.Column(db.Float(10, 6))
	confirmed = db.Column(db.Integer)
	recovered = db.Column(db.Integer)
	dead = db.Column(db.Integer)
	email = db.Column(db.String(320))
	status = db.Column(db.Integer)  # 0 = pending, -1 = denied, 1 = accepted
	
	def json_serializable(self):
		return {
			"data_id": self.data_id,
			"location": self.location,
			"latitude": float(self.latitude),
			"longitude": float(self.longitude),
			"confirmed": float(self.confirmed),
			"recovered": float(self.recovered),
			"dead": float(self.dead)
		}

class User(db.Model):
	__tablename__ = "users"
	user_id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(320))
	firstname = db.Column(db.String(32))
	lastname = db.Column(db.String(32))
	password_encrypt = db.Column(db.String(256))

def find_email(email):
	result = User.query.filter_by(email=email).first()
	return result

# miles
def calc_distance(latlong1, latlong2):
	return func.sqrt(func.pow(69.1 * (latlong1[0] - latlong2[0]),2)
				   + func.pow(53.0 * (latlong1[1] - latlong2[1]),2))


def find_cases(latitude, longitude, radius=250):
	result = Datapoint.query.filter(
		and_(
			calc_distance(
				(latitude, longitude),
				(Datapoint.latitude, Datapoint.longitude)
			) < radius, 
			Datapoint.status == 1
		)
	)
	return result.all()

def find_pending():
	result = Datapoint.query.filter(Datapoint.status == 0)
	return result.all()
