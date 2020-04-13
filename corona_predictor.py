import math
import numpy as np
import sys
import datetime
import json

import scipy.optimize

# import os

# os.environ['KERAS_BACKEND'] = 'cntk'

# from pandas import read_csv, DataFrame
# from keras.models import Sequential
# from keras.layers import Dense
# from keras.layers import LSTM
# from sklearn.preprocessing import MinMaxScaler
# from sklearn.metrics import mean_squared_error

# def create_dataset(dataset, look_back=1):
# 	dataX, dataY = [], []
# 	for i in range(len(dataset)-look_back-1):
# 		a = dataset[i:(i+look_back), 0]
# 		dataX.append(a)
# 		dataY.append(dataset[i + look_back, 0])
# 	return np.array(dataX), np.array(dataY)

# def do_code(inp_arr, advance, lookback=20, epochs=100):

# 	np.random.seed(7)

#     #dataframe = read_csv('test_data.csv', usecols=[2], engine='python')
# 	dataframe = DataFrame({"Series" : inp_arr})
# 	dataset = dataframe.values
# 	dataset = dataset.astype('float32')

# 	scaler = MinMaxScaler(feature_range=(0, 1))
# 	dataset = scaler.fit_transform(dataset)
# 	train_size = int(len(dataset) * 0.67)
# 	#test_size = len(dataset) - train_size
#     #train, test = dataset[0:train_size,:], dataset[train_size:len(dataset),:]
# 	look_back = lookback
# 	trainX, trainY = create_dataset(dataset, look_back)

# 	trainX = np.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))
#     #testX = np.reshape(testX, (testX.shape[0], 1, testX.shape[1]))

# 	model = Sequential()
# 	model.add(LSTM(4, input_shape=(1, look_back)))
# 	model.add(Dense(1))
# 	model.compile(loss='mean_squared_error', optimizer='adam')
# 	model.fit(trainX, trainY, epochs=epochs, batch_size=1, verbose=0)


# 	trainPredict = model.predict(trainX)
#     #testPredict = model.predict(testX)

# 	trainPredict = scaler.inverse_transform(trainPredict)
# 	trainY = scaler.inverse_transform([trainY]).tolist()[0]
#     #testPredict = scaler.inverse_transform(testPredict)
#     #testY = scaler.inverse_transform([testY])

# 	predArr = trainY[-look_back:]
# 	for i in range(advance+1):
# 		temp = np.array(predArr.copy())
# 		temp = np.reshape(temp, (1, look_back))
# 		temp = scaler.transform(temp)
# 		temp = np.reshape(temp, (temp.shape[0], 1, temp.shape[1]))
# 		predval = scaler.inverse_transform(model.predict(temp, verbose=0)).tolist()[0][0]
# 		if i > 0: trainY.append(predval)
# 		predArr.append(predval)
# 		predArr = predArr[1:]

# 	return trainY

# def predict_data(fixed_data, advance, lookback=20):
#     return do_code(fixed_data, advance=advance, lookback=lookback, epochs=10)

def logistic(t, MAX, T_INF, T_RISE):
    return MAX / (1 + np.exp(-(t - T_INF)/T_RISE))

if __name__ == "__main__":
    dates = []
    d = {}

    for date_ in sys.argv[1].split():
        year, month, day = date_.split('-')
        dates.append(datetime.date(int(year), int(month), int(day)))

    if not dates:
        print("data=" + json.dumps({"MAX": 0, "T_INF": 0, "T_RISE": 1, "x": [], "y": []}))
        exit()
    
    min_date = dates[0]

    X = np.array([(date_ - min_date).days for date_ in dates])
    Y = np.array([float(y) for y in sys.argv[2].split()])

    # paired = {X[i]: Y[i] for i in range(len(X))}

    # fixed_Y = []
    # i = 0
    # while i < (dates[-1] - dates[0]).days:
    #     if i not in paired:
    #         fixed_Y.append(fixed_Y[-1])
    #     else:
    #         fixed_Y.append(paired[i])
    #     i += 1
    
    # lookback = 5

    # x = list(range(len(fixed_Y) * 2))
    # y = predict_data(fixed_Y, len(fixed_Y), lookback)

    # d['x'] = x
    # d['y'] = [Y[0]] * lookback + y

    #               a       b   c               c/(1+ae^(-bx))
    bounds = (
        [
            max(Y), # top of regression must be at least the highest date seen
            0,      # the time of the inflection must be at least the starting date
            1       # the time to rise must be at least 1 day (to avoid exponential overflow)
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
            max(Y),           # max (default: max)
            X[len(X)//2],     # t_inf (default: middle value)
            30,                # t_rise (default: 30 days)
        ]),
        0, 7.3e9  # min and max values
    )

    try:
        (MAX, T_INF, T_RISE), cov = scipy.optimize.curve_fit(logistic, X, Y, p0=p0, maxfev=10000, bounds=bounds)
    except Exception as e:
        MAX, T_INF, T_RISE = list(p0)

    d['MAX'] = MAX
    d['T_INF'] = T_INF
    d['T_RISE'] = T_RISE

    # d = {"MAX": MAX, "T_INF": T_INF, "T_RISE": T_RISE}
    print("data=" + json.dumps(d))
    
