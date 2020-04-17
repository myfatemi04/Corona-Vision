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
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error

# DEBUG MARKER
port = 5050
if 'PORT' in os.environ:
	port = os.environ['PORT']
	
host = "0.0.0.0"

app = Flask(__name__)
cors = CORS(app)


def create_dataset(dataset, look_back=1):
	dataX, dataY = [], []
	for i in range(len(dataset)-look_back):
		a = dataset[i:(i+look_back), 0]
		dataX.append(a)
		dataY.append(dataset[i + look_back, 0])
	return np.array(dataX), np.array(dataY)

def do_code(inp_arr, advance, lookback=20, epochs=100):

	np.random.seed(7)

	#dataframe = read_csv('test_data.csv', usecols=[2], engine='python')
	dataframe = DataFrame({"Series" : inp_arr})
	dataset = dataframe.values
	dataset = dataset.astype('float32')

	scaler = MinMaxScaler(feature_range=(0, 1))
	dataset = scaler.fit_transform(dataset)
	train_size = int(len(dataset) * 0.67)
	#test_size = len(dataset) - train_size
	#train, test = dataset[0:train_size,:], dataset[train_size:len(dataset),:]
	look_back = lookback
	trainX, trainY = create_dataset(dataset, look_back)

	trainX = np.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))
	#testX = np.reshape(testX, (testX.shape[0], 1, testX.shape[1]))

	model = Sequential()
	model.add(LSTM(4, input_shape=(1, look_back), activation='tanh'))
	model.add(Dense(1))
	model.compile(loss='mean_squared_error', optimizer='adam')
	model.fit(trainX, trainY, epochs=epochs, batch_size=1, verbose=0)


	trainPredict = model.predict(trainX)
	#testPredict = model.predict(testX)

	trainPredict = scaler.inverse_transform(trainPredict)
	trainY = scaler.inverse_transform([trainY]).tolist()[0]
	#testPredict = scaler.inverse_transform(testPredict)
	#testY = scaler.inverse_transform([testY])

	predArr = trainY[-look_back:]
	for i in range(advance+1):
		temp = np.array(predArr.copy())
		temp = np.reshape(temp, (1, look_back))
		temp = scaler.transform(temp)
		temp = np.reshape(temp, (temp.shape[0], 1, temp.shape[1]))
		predval = scaler.inverse_transform(model.predict(temp, verbose=0)).tolist()[0][0]
		trainY.append(predval)
		predArr.append(predval)
		predArr = predArr[1:]

	return trainY

def predict_data(fixed_data, advance, lookback=20):
	return do_code(fixed_data, advance=advance, lookback=lookback, epochs=50)

def logistic(t, MAX, T_INF, T_RISE):
    return MAX / (1 + np.exp(-(t - T_INF)/T_RISE))

lstm_cache = {}
log_cache = {}

@app.route("/predict/lstm", methods=['POST'])
def predict_lstm():
	dates = []
	d = {}
	
	if "X" not in request.form or "Y" not in request.form:
		return {"X": [], "Y": []}
	rfx = request.form.get("X")
	rfy = request.form.get("Y")
	
	# rfx = "2020-02-24 2020-02-25 2020-02-26 2020-02-27 2020-02-28 2020-02-29 2020-03-01 2020-03-02 2020-03-03 2020-03-04 2020-03-05 2020-03-06 2020-03-07 2020-03-08 2020-03-09 2020-03-10 2020-03-11 2020-03-12 2020-03-13 2020-03-14 2020-03-15 2020-03-16 2020-03-17 2020-03-18 2020-03-19 2020-03-20 2020-03-21 2020-03-22 2020-03-23 2020-03-24 2020-03-25 2020-03-26 2020-03-27 2020-03-28 2020-03-29 2020-03-30 2020-03-31 2020-04-01 2020-04-02 2020-04-03 2020-04-04 2020-04-05 2020-04-06 2020-04-07 2020-04-08 2020-04-09 2020-04-10 2020-04-11 2020-04-12 2020-04-13" # = request.form.get("X")
	# rfy = "1 23 33 33 36 41 47 49 49 52 55 60 85 85 95 110 195 195 189 210 214 214 228 256 278 285 305 334 377 392 419 458 466 476 499 515 567 569 643 672 688 700 756 811 823 887 925 1040 1136 1348" # = request.form.get("Y")
	
	for date_ in rfx.split():
		year, month, day = date_.split('-')
		dates.append(datetime.date(int(year), int(month), int(day)))
	
	min_date = dates[0]
	
	X = np.array([(date_ - min_date).days for date_ in dates])
	Y = np.array([float(y) for y in rfy.split()])
	
	# print(" ".join(str(x) for x in X))
	# print(" ".join(str(y) for y in Y))
	
	key = (tuple(X), tuple(Y))
	
	if key in lstm_cache:
		return lstm_cache[key]
	
	paired = {X[i]: Y[i] for i in range(len(X))}

	fixed_Y = []
	i = 0
	while i < (dates[-1] - dates[0]).days:
		if i not in paired:
			fixed_Y.append(fixed_Y[-1])
		else:
			fixed_Y.append(paired[i])
		i += 1
	
	lookback = min(20, len(fixed_Y)//2)
	
	if len(fixed_Y) < 10:
		d['x'] = list(range(len(fixed_Y)))
		d['y'] = fixed_Y
		lstm_cache[key] = d
		return d
	
	x = list(range(len(fixed_Y) * 2))
	y = predict_data(fixed_Y, len(fixed_Y), lookback)
	future_data = y[len(fixed_Y) - lookback + 1:]

	d['x'] = x
	d['y'] = [point for point in fixed_Y] + [point for point in future_data]
	
	# print(x, fixed_Y)
	# print(d['y'])
	# print(y)
	
	lstm_cache[key] = d
	return d
	
@app.route("/predict/log", methods=['POST'])
def predict_log():
	
	dates = []
	d = {}
	
	if "X" not in request.form or "Y" not in request.form:
		return {"MAX": 0, "T_INF": 0, "T_RISE": 1}

	for date_ in request.form.get("X").split():
		year, month, day = date_.split('-')
		dates.append(datetime.date(int(year), int(month), int(day)))
		
	if not dates:
		return {"MAX": 0, "T_INF": 0, "T_RISE": 1}
	
	min_date = dates[0]
	
	X = np.array([(date_ - min_date).days for date_ in dates])
	Y = np.array([float(y) for y in request.form.get("Y").split()])
	
	key = (tuple(X), tuple(Y))
	if key in log_cache:
		return log_cache[key]
	
	bounds = (
		[
			Y[-1], # top of regression must be at least the highest date seen
			0,	  # the time of the inflection must be at least the starting date
			1	   # the time to rise must be at least 1 day (to avoid exponential overflow)
		],
		[
			7.3e9, # upper bound for MAX
			800,  # upper bound for T_INF
			800  # upper bound for T_RISE
		]
	)

	# starting values
	p0 = np.clip(
		np.array([
			Y[-1],		   # max (default: max)
			X[len(X)//2],	 # t_inf (default: middle value)
			30,				# t_rise (default: 30 days)
		]),
		0, 7.3e9  # min and max values
	)

	try:
		(MAX, T_INF, T_RISE), cov = scipy.optimize.curve_fit(logistic, X, Y, p0=p0, maxfev=10000, bounds=bounds)
	except Exception as e:
		print("Exception: ", e)
		MAX, T_INF, T_RISE = list(p0)

	d['MAX'] = MAX
	d['T_INF'] = T_INF
	d['T_RISE'] = T_RISE
	
	log_cache[key] = d
	
	return d

@app.route("/")
def redirect_to_coronavision():
	return redirect("http://www.coronavision.us")
	
if __name__ == "__main__":
	app.run(host, port, threaded=True, debug=True)
	