from flask import *
from werkzeug.security import generate_password_hash, check_password_hash
import os
import time
import datetime
from threading import Thread
import datetime
import json

import import_data
from corona_sql import *

app = Flask(__name__)
app.secret_key = os.environ['APP_SECRET_KEY']
app.static_folder = "./static"

sql_uri = "sqlite:///datapoints.db" #os.environ['DATABASE_URL']
app.config['SQLALCHEMY_DATABASE_URI'] = sql_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# used to initially create the database
if not os.path.isfile("datapoints.db"):
	with app.app_context():
		db.create_all()

def get_sorted_dates():
	dates = []
	session = db.session()
	for tup in session.query(Datapoint.entry_date).distinct():
		dates.append(tup[0])
	return sorted(dates, reverse=True)

@app.route("/")
def main_page():
	sorted_dates=get_sorted_dates()

	return render_template("main_page.html", sorted_dates=sorted_dates)

@app.route("/map")
def map_frontend():
	sorted_dates=get_sorted_dates()

	return render_template("map.html", sorted_dates=sorted_dates)

def get_bounding_box():
	ne_lat = float(request.args.get("ne_lat") or 90)
	ne_lng = float(request.args.get("ne_lng") or 180)
	sw_lat = float(request.args.get("sw_lat") or -90)
	sw_lng = float(request.args.get("sw_lng") or -180)
	return sw_lat, sw_lng, ne_lat, ne_lng

def parse_date(entry_date_str):
	try:
		year, month, day = entry_date_str.split("-")
		entry_date = datetime.date(int(year), int(month), int(day))
		return entry_date
	except:
		return None

def get_country_province_admin2():
	country = request.args.get("country") or ""
	province = request.args.get("province") or ""
	admin2 = request.args.get("admin2") or ""
	return {"country": country, "province": province, "admin2": admin2}

# example url:
# /cases/?ne_lat=...se_lat=...
@app.route("/cases/box")
def find_cases_backend():
	cases = find_cases_by_location(*get_bounding_box())
	entry_date = parse_date(request.args.get("date"))

	if entry_date:
		cases = cases.filter_by(
			entry_date=entry_date,
			is_primary=True,
			location_labelled=True
		)

		return json_list(cases.all())
	else:
		return "Please specify a date"

@app.route("/cases/totals/world")
def find_total_world_cases():
	cases = find_cases_by_location(*get_bounding_box())
	entry_date = parse_date(request.args.get("date"))
	if entry_date:
		cases = cases.filter_by(
			entry_date=entry_date,
			country=''
		)

		return json_list(cases.all())
	else:
		return "Please specify a date"

@app.route("/cases/totals")
def find_total_nation_cases():
	entry_date = parse_date(request.args.get("date"))
	sort = get_("sort", default="")
	if entry_date:
		nation = get_country_province_admin2()
		cases = find_cases_by_nation(**nation)
		cases = cases.filter_by(
			entry_date=entry_date
		)
		
		if sort:
			if sort == 'confirmed':
				cases = cases.order_by(Datapoint.confirmed.desc())
			elif sort == 'dconfirmed':
				cases = cases.order_by(Datapoint.dconfirmed.desc())

		return json_list(cases.all())
	else:
		return "Please specify a date"

@app.route("/cases/first_days")
def get_first_days():
	session = db.session()
	results = session.query(Datapoint).filter_by(is_first_day=True).order_by(Datapoint.entry_date).all()
	return json_list(results)

@app.route("/cases/totals_sequence")
def find_total_nation_cases_sequences():
	nation = get_country_province_admin2()

	session = db.session()
	results = session.query(Datapoint).filter_by(**nation).order_by(Datapoint.entry_date).all()

	return json_list(results)

def get_(key, default=True):
	return default if key not in request.args else request.args.get(key)

@app.route("/cases/date")
def find_all_for_date():
	entry_date = parse_date(request.args.get("date"))

	location_labelled = get_("location_labelled", default=1)
	is_primary = get_("is_primary", default=1)
	is_first_day = get_("is_first_day", default=0)

	country = get_("country", default="all")
	province = get_("province", default="all")
	admin2 = get_("admin2", default="all")

	session = db.session()
	results = session.query(Datapoint).filter_by(
		entry_date=entry_date,
		location_labelled=location_labelled,
		is_primary=is_primary,
		is_first_day=is_first_day
	)
	
	results = filter_by_nation(results, country, province, admin2)

	return json_list(results.all())

@app.route("/list/countries")
def list_all_countries():
	sess = db.session()
	entry_date = parse_date(request.args.get("date"))
	need_province = get_("need_province", "1")
	
	results = sess.query(Datapoint.country).filter(Datapoint.entry_date==entry_date)

	if need_province == "1":
		results = results.filter(Datapoint.province != '')

	return json.dumps(sorted([
		result[0]
		for result in results.distinct().all()
		if result[0]
	]))

@app.route("/list/provinces")
def list_country_provinces():
	sess = db.session()
	country = request.args.get("country") or ""
	entry_date = parse_date(request.args.get("date"))
	need_admin2 = get_("need_admin2", True)
	results = sess.query(Datapoint.province).filter(
		Datapoint.entry_date==entry_date, Datapoint.country==country
	)

	if need_admin2 == "1":
		results = results.filter(Datapoint.admin2 != '')
	
	return json.dumps(sorted([
		result[0]
		for result in results.distinct().all()
		if result[0]
	]))

@app.route("/list/admin2")
def list_province_admin2():
	sess = db.session()
	province = request.args.get("province") or ""
	country = request.args.get("country") or ""
	return json.dumps(sorted([
		result[0]
		for result in sess.query(Datapoint.admin2)\
		.filter_by(country=country, province=province)\
		.distinct()\
		.all()
		if result[0]
	]))

@app.route("/charts")
def charts_data_page():
	return render_template("charts.html", sorted_dates=get_sorted_dates())
	
@app.route("/whattodo")
def what_to_do_page():
	return render_template("whattodo.html")

@app.route("/recent")
def recent_page():
	return render_template("recent.html")

@app.route("/estimaterisk", methods=['GET', 'POST'])
def estimate_risk_page():
	if "submitted" in request.form:
		if "age" not in request.form:
			return render_template("estimate_risk.html", need_fields=True)

		age = int(request.form.get("age"))
		age_bracket = min(age // 10, 8)
		age_dangers = ["none", "low", "low", "low", "low", "slight", "moderate", "moderate-high", "high"]
		age_percents = [0, 0.2, 0.2, 0.2, 0.4, 1.3, 3.6, 8.0, 14.8]

		symptoms_text = (request.form.get("symptoms") or "").lower()
		possible_mild_symptoms = [
			"fever",
			"cough"
		]
		possible_severe_symptoms = [
			"shortness of breath",
			"trouble breathing",
			"hard breathing",
			"difficulty breathing",
			"difficult breathing",
			"hard to breathe",
			"body temperature",
			"high temperature",
			"chest pain",
			"chest pressure",
			"pressure in chest",
			"pain in chest",
		]

		mild_symptoms = [symptom.capitalize() for symptom in possible_mild_symptoms if symptom in symptoms_text]
		severe_symptoms = [symptom.capitalize() for symptom in possible_severe_symptoms if symptom in symptoms_text]

		return render_template("estimate_risk.html",
			age=age,
			age_danger=age_dangers[age_bracket],
			age_mortality=age_percents[age_bracket],
			mild_symptoms=mild_symptoms,
			severe_symptoms=severe_symptoms
		)
	else:
		return render_template("estimate_risk.html")

@app.route("/history")
def history_page():
	return render_template("spread_history.html")

@app.route("/map_frame")
def map_frame():
	sorted_dates=get_sorted_dates()

	return render_template("map_frame.html", sorted_dates=sorted_dates)

@app.route("/contact")
def contact_page():
	return render_template("contact.html")

@app.route("/data")
def data_page():
	# country = request.args.get("country")
	# province = request.args.get("province")
	# label = "country"

	# if country:
	# 	province = "all"
	# 	label = "province"
	# else:
	# 	province = ""
	# 	country = "all"
	
	# session = db.session()
	# results = session.query(Datapoint).filter_by(entry_date='2020-04-07')
	# results = filter_by_nation(results, country, province, '')
	# results = results.order_by(Datapoint.confirmed.desc())
	# location_rows = results.all()

	# return render_template("data.html", sorted_dates=get_sorted_dates(), label=label, location_rows=location_rows)

	return render_template("data.html", sorted_dates=get_sorted_dates())

@app.before_first_request
def start_downloader():
	data_download_thread = Thread(target=import_data.data_download, daemon=True)
	data_download_thread.start()

if __name__ == "__main__":
	if 'PORT' in os.environ:
		port = os.environ['PORT']
	else:
		port = 4040
	app.run(host='0.0.0.0', port=port, threaded=True, debug=True)
	
