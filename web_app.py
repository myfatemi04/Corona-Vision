from flask import *
from werkzeug.security import generate_password_hash, check_password_hash
import os
import time
from threading import Thread
from sqlalchemy import and_
import datetime

import import_data
import corona_sql

app = Flask(__name__)
app.secret_key = "10a765caa15fd56b4a95"
app.static_folder = "./static"

sql_uri = "mysql://root:jinny2yoo@35.226.226.204/corona"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = sql_uri
# app.wsgi_app = WhiteNoise(
# 	app.wsgi_app,
# 	root="static/",
# 	prefix="static/"
# )

corona_sql.db.init_app(app)

@app.route("/")
def main_page():
	return render_template("main_page.html")

@app.route("/findnearme")
def find_cases_frontend():
	data_entries = corona_sql.DataEntry.query.all()
	sorted_data_entries = sorted(
		data_entries,
		key=lambda x: x.entry_date,
		reverse=True
	)
	return render_template("find_cases.html", sorted_data_entries=sorted_data_entries)

# example url:
# /cases/38.9349376/-77.1909653
# = http://localhost:4040/cases/38.9349376/-77.1909653
@app.route("/cases")
def find_cases_backend():
	ne_lat = float(request.args.get("ne_lat"))
	ne_lng = float(request.args.get("ne_lng"))
	sw_lat = float(request.args.get("sw_lat"))
	sw_lng = float(request.args.get("sw_lng"))
	
	entry_date_str = request.args.get("date")
	year, month, day = entry_date_str.split("-")
	entry_date = datetime.date(int(year), int(month), int(day))
	cases = corona_sql.find_cases(ne_lat, ne_lng, sw_lat, sw_lng, entry_date)
	
	return json.dumps([case.json_serializable() for case in cases])

@app.route("/visual")
def visual_data_page():
	return render_template("visual.html")
	
@app.route("/whattodo")
def what_to_do_page():
	return render_template("whattodo.html")

@app.route("/recent")
def recent_page():
	return render_template("recent.html")

@app.route("/calculaterisk", methods=['GET', 'POST'])
def calculate_risk_page():
	if "submitted" in request.form:
		if "age" not in request.form:
			return render_template("calculate_risk.html", need_fields=True)
		age = int(request.form.get("age"))
		age_bracket = min(age // 10, 8)
		age_dangers = [
			"none", "low", "low", "low", "low", "slight", "moderate", "moderate-high", "high"
		]
		age_percents = [
			0, 0.2, 0.2, 0.2, 0.4, 1.3, 3.6, 8.0, 14.8
		]
		return render_template("calculate_risk.html",
			age=age,
			age_danger=age_dangers[age_bracket],
			age_mortality=age_percents[age_bracket]
		)
	else:
		return render_template("calculate_risk.html")

'''
# FEATURES THAT I'M PLANNING TO REMOVE #
@app.route("/register", methods=["GET", "POST"])
def register():
	if request.method == "GET":
		return render_template("register.html")
	email = request.form.get("email")
	firstname = request.form.get("firstname")
	lastname = request.form.get("lastname")
	password_encrypt = generate_password_hash(request.form.get("password"))
	
	if not all(
		(
			firstname,
			lastname,
			email,
			request.form.get("password")
		)
	):
		return render_template("register.html", message="Please fill out all fields")
	
	if corona_sql.find_email(email):
		return render_template("register.html", message="Username already taken")
	
	new_user = corona_sql.User(
		firstname=firstname,
		lastname=lastname,
		email=email,
		password_encrypt=password_encrypt,
		
	)
	
	corona_sql.db.session.add(new_user)
	corona_sql.db.session.commit()
	
	session['email'] = email
	
	return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "GET":
		return render_template("login.html")
	
	email = request.form.get("email")
	password = request.form.get("password")
	
	user = corona_sql.find_email(email)
	
	if not user:
		return render_template("login.html", message="Username or password is incorrect")
	
	if check_password_hash(user.password_encrypt, password):
		session['email'] = user.email
		return redirect("/")
	else:
		return render_template("login.html", message="Username or password is incorrect")

@app.route("/logout")
def logout():
	if 'email' in session:
		del session['email']
		
	return redirect("/")


@app.route("/submit_data_csv", methods=['GET', 'POST'])
def submit_data_csv():
	if request.method == 'GET':
		return render_template("submit_data_csv.html")
	else:
		if 'data' not in request.files:
			return render_template("submit_data_csv.html", message="Please attach a file")
			
		file = request.files['data']
		filename = "./data_uploads/" + str(time.time()) + file.filename
		file.save(filename)
		
		return render_template("submit_data_csv_complete.html")
@app.route("/submit_data", methods=['GET', 'POST'])
def submit_data():
	if request.method == 'GET':
		return render_template("submit_data_manual.html")
	else:
		location = request.form.get("location")
		latitude = request.form.get("latitude")
		longitude = request.form.get("longitude")
		confirmed = request.form.get("confirmed")
		recovered = request.form.get("recovered")
		dead = request.form.get("dead")
		email = request.form.get("email")
		if not all((location, latitude, longitude, confirmed, recovered, dead, email)):
			return abort(400)
		
		datapoint = corona_sql.Datapoint(
			location=location,
			latitude=latitude,
			longitude=longitude,
			confirmed=confirmed,
			recovered=recovered,
			dead=dead,
			email=email,
			status=0
		)
		corona_sql.db.session.add(datapoint)
		corona_sql.db.session.commit()
		return "", 200

@app.route("/approve_data", methods=['GET', 'POST'])
def approve_data():
	if 'email' not in session:
		return abort(403)
		
	if request.method == 'GET':
		pending_data = corona_sql.find_pending()
		return render_template("approve_data.html", pending_data=pending_data)
	else:
		data_id = request.form.get("data_id")
		if not data_id:
			return abort(400)
		
		
		found_data = corona_sql.Datapoint.query.filter(corona_sql.Datapoint.data_id == data_id).first()
		if not found_data:
			return abort(400)
		
		previous_datapoints = corona_sql.Datapoint.query.filter(
			and_(
				corona_sql.Datapoint.location == found_data.location,
				corona_sql.Datapoint.status == 1  # old data that was approved
			)
		).all()
		
		for old_data in previous_datapoints:
			corona_sql.db.session.delete(old_data)
		
		
		found_data.status = 1
		corona_sql.db.session.commit()
		return "", 200
'''



if __name__ == "__main__":
	data_download_thread = Thread(target=import_data.data_download, daemon=True)
	data_download_thread.start()
	
	if 'PORT' in os.environ:
		port = os.environ['PORT']
	else:
		port = 4040
	app.run(host='0.0.0.0', port=port, threaded=True, debug=True)
	
