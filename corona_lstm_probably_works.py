import numpy
import matplotlib.pyplot as plt
from pandas import read_csv, DataFrame
import math
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error

def create_dataset(dataset, look_back=1):
	dataX, dataY = [], []
	for i in range(len(dataset)-look_back-1):
		a = dataset[i:(i+look_back), 0]
		dataX.append(a)
		dataY.append(dataset[i + look_back, 0])
	return numpy.array(dataX), numpy.array(dataY)

def do_code(inp_arr, adv, lb, ep, graph):

	numpy.random.seed(7)

    #dataframe = read_csv('test_data.csv', usecols=[2], engine='python')
	dataframe = DataFrame({"Series" : inp_arr})
	dataset = dataframe.values
	dataset = dataset.astype('float32')

	scaler = MinMaxScaler(feature_range=(0, 1))
	dataset = scaler.fit_transform(dataset)
	train_size = int(len(dataset) * 0.67)
	test_size = len(dataset) - train_size
    #train, test = dataset[0:train_size,:], dataset[train_size:len(dataset),:]
	look_back = lb
	trainX, trainY = create_dataset(dataset, look_back)

	trainX = numpy.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))
    #testX = numpy.reshape(testX, (testX.shape[0], 1, testX.shape[1]))

	model = Sequential()
	model.add(LSTM(4, input_shape=(1, look_back)))
	model.add(Dense(1))
	model.compile(loss='mean_squared_error', optimizer='adam')
	model.fit(trainX, trainY, epochs=ep, batch_size=1, verbose=0)


	trainPredict = model.predict(trainX)
    #testPredict = model.predict(testX)

	trainPredict = scaler.inverse_transform(trainPredict)
	trainY = scaler.inverse_transform([trainY]).tolist()[0]
    #testPredict = scaler.inverse_transform(testPredict)
    #testY = scaler.inverse_transform([testY])

	predArr = trainY[-look_back:]
	for i in range(adv+1):
		temp = numpy.array(predArr.copy())
		temp = numpy.reshape(temp, (1, look_back))
		temp = scaler.transform(temp)
		temp = numpy.reshape(temp, (temp.shape[0], 1, temp.shape[1]))
		predval = scaler.inverse_transform(model.predict(temp, verbose=0)).tolist()[0][0]
		if i > 0: trainY.append(predval)
		predArr.append(predval)
		predArr = predArr[1:]

	if graph:
		plt.plot(trainY)
		plt.plot(trainPredict, "bo")
		plt.show()

	return trainY

def from_csv():
    df = read_csv("test_data.csv", usecols=[2], engine="python")
    print(do_code(df["Cases"].tolist(), 10, 20, 10, True))

from_csv()
