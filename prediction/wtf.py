import numpy
import matplotlib.pyplot as plt
from pandas import read_csv, DataFrame
import math
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Dense, concatenate
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import Conv1D
from tensorflow.keras.layers import MaxPooling1D
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
import random

def get_model(look_back):

	#Model 1 : Two layer LSTM
	model1 = Sequential()
	model1.add(LSTM(16, input_shape=(1, look_back), activation='tanh', return_sequences=True))
	model1.add(LSTM(8, activation='relu'))
	model1.add(Dense(1))

	#Model 2: Single layer LSTM
	model2 = Sequential()
	model2.add(LSTM(4, input_shape=(1, look_back), activation='relu'))
	model2.add(Dense(1))

	#Model 3: 1D convolutional neural net
	model3 = Sequential()
	model3.add(Conv1D(filters=64, kernel_size=5, activation='relu', input_shape=(look_back, 1)))
	model3.add(MaxPooling1D(pool_size=5))
	model3.add(Flatten())
	model3.add(Dense(50, activation='sigmoid'))
	model3.add(Dense(1))

	#Model 4: Multi-Layer 1D cnn
	model4 = Sequential()
	model4.add(Conv1D(filters=16, kernel_size=5, activation='relu', input_shape=(look_back, 1), padding="same"))
	model4.add(Conv1D(filters=32, kernel_size=5, activation='relu', padding="same"))
	model4.add(Conv1D(filters=32, kernel_size=5, activation='relu', padding="same"))
	model4.add(Conv1D(filters=64, kernel_size=5, activation='relu'))
	model4.add(MaxPooling1D(pool_size=5))
	model4.add(Flatten())
	model4.add(Dense(50, activation='sigmoid'))
	model4.add(Dense(1))

	#Model 5: Dual-Layer 1D cnn
	model5 = Sequential()
	model5.add(Conv1D(filters=64, kernel_size=5, activation='relu', input_shape=(look_back, 1)))
	model5.add(MaxPooling1D(pool_size=5))
	model5.add(Flatten())
	model5.add(Dense(50, activation='sigmoid'))
	model5.add(Dense(1))

	#Merge Models
	modeltmp = concatenate([model1.output, model2.output, model3.output, model4.output], axis=-1)
	modeltmp = Dense(1)(modeltmp)

	model = Model(inputs=[model1.input, model2.input, model3.input, model4.input], outputs=modeltmp)

	return model



def create_dataset(dataset, look_back=1):
	dataX, dataY = [], []
	for i in range(len(dataset)-look_back-1):
		a = dataset[i:(i+look_back), 0]
		dataX.append(a)
		dataY.append(dataset[i + look_back, 0])

	#dataR = [[dataX[i], dataY[i]] for i in range(len(dataX))]
	#random.shuffle(dataR)

	#return numpy.array([i[0] for i in dataR]), numpy.array([i[1] for i in dataR])
	return numpy.array(dataX), numpy.array(dataY)

def get_lstm(look_back):
	model = Sequential()
	model.add(LSTM(16, input_shape=(1, look_back), activation='relu', return_sequences=True))
	model.add(LSTM(8,  activation="tanh"))
	model.add(Dense(1))

	return model


def get_cnn(look_back):
	model = Sequential()
	model.add(Conv1D(filters=64, kernel_size=2, activation='relu', input_shape=(1, look_back)))
	model.add(MaxPooling1D(pool_size=2))
	model.add(Flatten())
	model.add(Dense(50, activation='relu'))
	model.add(Dense(1))

	return model


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

	trainXConv = trainX.copy()
	trainXConv = numpy.reshape(trainXConv, (trainXConv.shape[0], trainXConv.shape[1], 1))

	trainX = numpy.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))
    #testX = numpy.reshape(testX, (testX.shape[0], 1, testX.shape[1]))

	print(trainX.shape)

	model = get_lstm(look_back)

	model.compile(loss='mean_squared_error', optimizer='adam')

	#model.fit([trainX, trainX, trainXConv, trainXConv], trainY, epochs=ep, batch_size=1, verbose=2)
	model.fit(trainX, trainY, epochs=ep, batch_size=1, verbose=2)

	#trainPredict = model.predict([trainX, trainX, trainXConv, trainXConv])
	trainPredict = model.predict(trainX)

    #testPredict = model.predict(testX)
	trainPredict = scaler.inverse_transform(trainPredict)
	trainY = scaler.inverse_transform([trainY]).tolist()[0]
    #testPredict = scaler.inverse_transform(testPredict)
    #testY = scaler.inverse_transform([testY])

	predArr = trainY[-look_back:]

	trainer = trainY.copy()
	for i in range(adv+1):
		temp = numpy.array(predArr.copy())
		temp = numpy.reshape(temp, (1, look_back))
		temp = scaler.transform(temp)
		temp2 = temp.copy()
		temp2 = numpy.reshape(temp2, (1, temp2.shape[1], temp2.shape[0]))
		temp = numpy.reshape(temp, (temp.shape[0], 1, temp.shape[1]))
		#predval = scaler.inverse_transform(model.predict([temp, temp, temp2, temp2], verbose=0)).tolist()[0][0]
		predval = scaler.inverse_transform(model.predict(temp, verbose=2)).tolist()[0][0]

		if i > 0: trainY.append(predval)

		predArr.append(predval)
		predArr = predArr[1:]

	if graph:
		plt.plot(trainY, "bo")
		#plt.plot(trainPredict, "go")
		plt.plot(trainer, "go")
		plt.show()

	return trainY


def do_code2(inp_arr, advance, lookback=20, epochs=100):

	numpy.random.seed(7)

	print("INP_ARR: "+ str(inp_arr[0]))

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

	print("TRAINY: " + str(trainY[0]))

	trainX = numpy.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))
	#testX = np.reshape(testX, (testX.shape[0], 1, testX.shape[1]))

	model = get_model()

	model.compile(loss='mean_squared_error', optimizer='adam')
	model.fit(trainX, trainY, epochs=epochs, batch_size=1, verbose=2)


	trainPredict = model.predict(trainX)
	#testPredict = model.predict(testX)

	trainPredict = scaler.inverse_transform(trainPredict)
	trainY = scaler.inverse_transform([trainY]).tolist()[0]
	#testPredict = scaler.inverse_transform(testPredict)
	#testY = scaler.inverse_transform([testY])

	predArr = trainY[-look_back:]

	trainer = trainY.copy()
	print(trainer[0])

	for i in range(advance+1):
		temp = numpy.array(predArr.copy())
		temp = numpy.reshape(temp, (1, look_back))
		temp = scaler.transform(temp)
		temp = numpy.reshape(temp, (temp.shape[0], 1, temp.shape[1]))
		predval = scaler.inverse_transform(model.predict(temp, verbose=0)).tolist()[0][0]
		trainY.append(predval)
		predArr.append(predval)
		predArr = predArr[1:]

	arr = [1.0,23.0,33.0,33.0,36.0,41.0,47.0,49.0,49.0,52.0,55.0,60.0,85.0,85.0,95.0,110.0,195.0,195.0,189.0,210.0,213.99999015621168,213.99999015621168,227.99999768770073,255.99999583786132,278.00000284082483,284.9999981501606,305.00001374166425,334.0000160539635,377.0000089849343,392.00002067856207,419.000014666584,458.00002477463505,466.0000242461095,475.9999982162263,499.0000093813285,515.0000083242774,567.0000218016788,568.9999963003212,642.9999998678686,672.0000021801679,688.0000011231168,699.999983417511,755.999945892197,810.999954943197,823.0000048888613,887.000000660657,924.9999896937518,1039.9999778679926,1135.999971525686,1096.300048828125,1144.3382568359375,1191.37548828125,1233.35888671875,1277.448974609375,1307.80419921875,1337.6685791015625,1367.4278564453125,1393.276123046875,1420.194580078125,1435.4637451171875,1448.7218017578125,1461.782958984375,1473.984375,1480.152099609375,1486.6214599609375,1489.9024658203125,1494.0340576171875,1498.1121826171875,1500.4637451171875,1502.264404296875,1504.5455322265625,1506.419677734375,1508.2119140625,1509.7159423828125,1511.035400390625,1512.1324462890625,1513.070068359375,1513.8853759765625,1514.652099609375,1515.1507568359375,1515.5938720703125,1515.9761962890625,1516.275146484375,1516.5091552734375,1516.702392578125,1516.8409423828125,1516.98095703125,1517.0955810546875,1517.1846923828125,1517.266357421875,1517.342041015625,1517.4056396484375,1517.4625244140625,1517.5098876953125,1517.5521240234375,1517.586181640625,1517.6146240234375,1517.6396484375,1517.66064453125]

	arr2 = [1.0,23.0,33.0,33.0,36.0,41.0,47.0,49.0,49.0,52.0,55.0,60.0,85.0,85.0,95.0,110.0,195.0,195.0,189.0,210.0,214.0,214.0,228.0,256.0,278.0,285.0,305.0,334.0,377.0,392.0,419.0,458.0,466.0,476.0,499.0,515.0,567.0,569.0,643.0,672.0,688.0,700.0,756.0,811.0,823.0,887.0,925.0,1040.0,1136.0,1094.5162353515625,1172.49755859375,1187.20263671875,1220.51318359375,1272.75048828125,1297.5484619140625,1335.218017578125,1387.2374267578125,1451.7703857421875,1489.4774169921875,1530.0411376953125,1592.6541748046875,1638.5562744140625,1700.772705078125,1726.7515869140625,1768.482177734375,1842.4337158203125,1877.449951171875,1903.841796875,1960.3270263671875,2001.7921142578125,2033.4581298828125,2074.774658203125,2104.8037109375,2128.17236328125,2151.219482421875,2176.015625,2194.8134765625,2217.511474609375,2238.057373046875,2249.2216796875,2264.1357421875,2276.386474609375,2283.672607421875,2293.845458984375,2304.495361328125,2312.346435546875,2320.04150390625,2327.126220703125,2333.281494140625,2338.567138671875,2343.841552734375,2348.501953125,2352.439208984375,2356.6455078125,2359.727783203125,2362.5615234375,2365.389892578125,2367.488037109375]


	#plt.plot(arr)

	#plt.plot(arr2)

	plt.plot(inp_arr, "yo")

	plt.plot(trainY, "bo")
	#plt.plot(trainPredict, "go")
	plt.plot(trainer, "go")
	plt.show()


	print([int(i) for i in trainY])
	print([int(i) for i in trainer])
	print([int(i) for i in inp_arr])

	return trainY




def from_csv():
	df = read_csv("test_data.csv", usecols=[2], engine="python")
	lb = int(len(df["Cases"].tolist()) / 3)
	print(do_code(df["Cases"].tolist(), 150, 10, 100, True))

world = "1.0 23.0 33.0 33.0 36.0 41.0 47.0 49.0 49.0 52.0 55.0 60.0 85.0 85.0 95.0 110.0 195.0 195.0 189.0 210.0 214.0 214.0 228.0 256.0 278.0 285.0 305.0 334.0 377.0 392.0 419.0 458.0 466.0 476.0 499.0 515.0 567.0 569.0 643.0 672.0 688.0 700.0 756.0 811.0 823.0 887.0 925.0 1040.0 1136.0 1348.0".split()

world = [float(i) for i in world]

belarus = "1.0, 1.0, 1.0, 1.0, 1.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 9.0, 9.0, 12.0, 27.0, 27.0, 27.0, 36.0, 36.0, 51.0, 51.0, 69.0, 76.0, 76.0, 81.0, 81.0, 86.0, 86.0, 94.0, 94.0, 94.0, 152.0, 152.0, 163.0, 304.0, 351.0, 440.0, 562.0, 700.0, 861.0, 1066.0, 1486.0, 1981.0, 2226.0, 2578.0".split(", ")

belarus = [float(i) for i in belarus]

#random.shuffle(belarus)

#print(do_code(world, 30, 20, 20, True))
#do_code2(belarus,len(belarus), lookback=20)

from_csv()
