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
app.secret_key = os.environ['APP_SECRET_KEY']
app.static_folder = "./static"

sql_uri = os.environ['DATABASE_URL']
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

@app.route("/cases/total/<string:country>/<string:datestr>")
def find_country_total(country, datestr):
	year, month, day = datestr.split("-")
	results = corona_sql.find_country_total(country, datetime.date(int(year), int(month), int(day)))
	return json.dumps(results)

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

if __name__ == "__main__":
	data_download_thread = Thread(target=import_data.data_download, daemon=True)
	data_download_thread.start()
	
	if 'PORT' in os.environ:
		port = os.environ['PORT']
	else:
		port = 4040
	app.run(host='0.0.0.0', port=port, threaded=True, debug=True)
	
