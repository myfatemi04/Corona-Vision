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

sql_uri = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_DATABASE_URI'] = sql_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route("/")
def main_page():
	return render_template("main_page.html")

@app.route("/findnearme")
def find_cases_frontend():
	dates = []
	session = db.session()
	for tup in session.query(Datapoint.entry_date).distinct():
		dates.append(tup[0])
	
	return render_template("find_cases.html", sorted_dates=sorted(dates, reverse=True))

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
	if entry_date:
		nation = get_country_province_admin2()
		cases = find_cases_by_nation(**nation)
		cases = cases.filter_by(
			entry_date=entry_date
		)

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

@app.route("/list/countries")
def list_all_countries():
	sess = db.session()
	return json.dumps(sorted([
		result[0]
		for result in sess.query(Datapoint.country).distinct().all()
		if result[0]
	]))

@app.route("/list/provinces")
def list_country_provinces():
	sess = db.session()
	country = request.args.get("country") or ""
	return json.dumps(sorted([
		result[0]
		for result in sess.query(Datapoint.province).filter_by(country=country).distinct().all()
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

@app.route("/history")
def history_page():
	return render_template("spread_history.html")

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
	
