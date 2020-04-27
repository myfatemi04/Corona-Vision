from flask import Flask, request, redirect
from flask_cors import CORS
import os
import sys
import datetime
import time
import numpy as np
import scipy.optimize

from pandas import read_csv, DataFrame
import math
import corona_sql

# DEBUG MARKER
port = 5050
if 'PORT' in os.environ:
	port = os.environ['PORT']
	
host = "0.0.0.0"

app = Flask(__name__)
cors = CORS(app)

def logistic(t, LNMAX, T_INF, T_RISE, LIN):
	return np.exp(LNMAX) / (1 + np.exp(-(t - T_INF)/(T_RISE + LIN * t)))
	# return np.exp(LNMAX) / (1 + np.exp(-(t - T_INF)/(T_RISE * (1 + LIN * (t - T_INF) / T_RISE))))
	# return np.exp(LNMAX) / (1 + np.exp(-(t - T_INF)/(T_RISE * (1 + np.exp((t - T_INF)/LIN)))))
	# return np.exp(LNMAX) / (1 + np.exp(-(t - T_INF)/T_RISE))

log_cache = {}

@app.route("/predict/log")
def predict_log():
	country = request.args.get("country") or ""
	province = request.args.get("province") or ""
	county = request.args.get("county") or ""

	X, Y = corona_sql.time_series(country, province, county)

	if not X or len(X) < 10:
		return {"LNMAX": 0, "MAX": 1, "T_INF": 0, "T_RISE": 1, "LIN": 0}

	if (country, province, county) in log_cache and time.time() - log_cache[country, province, county]['time'] < (60 * 360 * 12):
		return log_cache[country, province, county]['pred']

	min_date = min(X)
	numbered_X = [(x - min_date).days for x in X]
	
	bounds = (
		[
			np.log(Y[-1]), # top of regression must be at least the highest date seen
			0,	# the time of the inflection must be at least the starting date
			1,	# the time to rise must be at least 1 day (to avoid exponential overflow)
			0
		],
		[
			np.log(7.3e9), # upper bound for MAX
			800,# upper bound for T_INF
			800,# upper bound for T_RISE
			20
		]
	)

	# starting values
	p0 = np.clip(
		np.array([
			# max (default: max)
			np.log(Y[-1]),

			# t_inf (default: middle value)
			numbered_X[len(X)//2],

			# t_rise (default: 30 days)
			40,

			# linear change
			1
		]),
		0, 7.3e9# min and max values
	)

	try:
		(LNMAX, T_INF, T_RISE, LIN), _ = scipy.optimize.curve_fit(logistic, numbered_X, Y, p0=p0, maxfev=10000, bounds=bounds)
	except Exception as e:
		print("Exception: ", e, type(e))
		LNMAX, T_INF, T_RISE, LIN = list(p0)

	d = {}
	d['LNMAX'] = LNMAX
	d['MAX'] = np.exp(LNMAX)
	d['T_INF'] = T_INF
	d['T_RISE'] = T_RISE
	d['LIN'] = LIN

	log_cache[country, province, county] = {"time": time.time(), "pred": d}

	return d

statisticThres = 30

@app.route("/predict/seir")
def predict_seir():
	import json
	import scipy.stats
	country = request.args.get("country") or ""
	province = request.args.get("province") or ""
	county = request.args.get("county") or ""

	X, Y = corona_sql.timeSeriesAll(country, province, county)
	recoveryRates = np.array([])
	removalRates = np.array([])
	tTimesC = np.array([])
	for row in Y:
		drecovered = row.drecovered
		ddeaths = row.ddeaths
		active = row.active
		if row.total <= statisticThres:
			continue
		if active <= 0:
			continue
		if ddeaths + drecovered <= 0:
			continue
		if drecovered <= 0:
			continue
		recoveryRate = drecovered/active
		removalRate = (drecovered + ddeaths)/active
		# infections per day = contacts / day* susc/total * Transmission probability * infected
		# dtotal = (Contacts) * (S/total) * (Transmission) * I
		S = (7.3e9 - row.total)
		tTimesC = np.append(tTimesC, [row.dtotal / (S/7.3e9 * active)], axis=0)
		recoveryRates = np.append(recoveryRates, [recoveryRate], axis=0)
		removalRates = np.append(removalRates, [removalRate], axis=0)

	# the first day where we mention recoveries will be a spike
	if len(recoveryRates) > 0:
		recoveryRates = recoveryRates[1:]

	if len(removalRates) > 0:
		removalRates = removalRates[1:]

	if len(tTimesC) > 0:
		tTimesC = tTimesC[1:]

	recoveryProbability = scipy.stats.gmean(recoveryRates)
	removalProbability = scipy.stats.gmean(removalRates)

	# World overall recoveryProbability = 0.020244933251719263
	# World overall removalProbability = 0.026082348497932107
	# Each day, there is a 2.61% chance of recovering OR dying.
	# This means that is a 5% chance of not recoverying/dying after
	# 97.39% ^ X = 0.05 --> X = 113 days
	# 97.39% ^ X = 0.5 --> X = 26.2 days for the majority
	# 97.39% ^ X = 0.95 --> X = 2 days for 5% of people
	
	infectionRate = 0.01

	return {
		"recoveryRates": list(recoveryRates),
		"recoveryProbability": recoveryProbability,
		"removalRates": list(removalRates),
		"removalProbability": removalProbability,
		"tTimesC": list(tTimesC)
	}

def dynamicSEIR(X, Y):
	S = 12000000
	E = 0
	I = 1
	R = 0
	for x in range(1, len(Y)):
		# print("{:.2f} {:.2f} {:.2f} {:.2f}".format(S, E, I, R))
		yesterdayActive = Y[x - 1].total - Y[x - 1].deaths - Y[x - 1].recovered
		todayRemoved = Y[x].recovered + Y[x].deaths
		removalProbabilityToday = todayRemoved/yesterdayActive
		# recoveriesToday = I * removalProbabilityToday
		print(removalProbabilityToday)

		# casesToday = I * contacts * S / (S + E + I + R) * infectionRate
		# infectionRateContactsProportion = 

		# # these equations should be in equilibrium
		# R = R + recoveriesToday
		# I = I + casesToday - recoveriesToday
		# S = S - casesToday

@app.route("/")
def redirect_to_coronavision():
	return """
This is our backend<br/>
If you're curious and wanna test it out use this form:<br/>
<form action="/predict/seir" method="get">
	Country:<br/>
	<input type="text" name="country"><br/>
	Province:<br/>
	<input type="text" name="province"><br/>
	County:<br/>
	<input type="text" name="county"><br/>
	<button type="submit">Test</button>
</form>
	"""

# X, Y = corona_sql.timeSeriesAll("United States", "", "")
# dynamicSEIR(X, Y)

if __name__ == "__main__":
	app.run(host, port, threaded=True, debug=True)
