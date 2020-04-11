import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from keras.models import Sequential
from keras.layers import Dense, LSTM
import matplotlib.pyplot as plt
import sys

def create_dataset(dataset, look_back=1):
    look_back=1
    """creates dataset with lookback of 1 timestep"""
    dataX, dataY = [], []
    for i in range(len(dataset)-look_back-1):
        a = dataset[i:(i+look_back), 0]
        dataX.append(a)
        dataY.append(dataset[i + look_back, 0])
    return np.array(dataX), np.array(dataY)

def create_dataX(data_X, look_back=1):
    look_back=1
    dataX = []
    for i in range(len(data_X)-look_back-1):
        a = data_X[i:(i+look_back)]
        dataX.append(a)
    return np.array(dataX)


def do_code(data, adv, mx):
    look_back=1
    """init scalers for data normalization"""
    xscl = MinMaxScaler(feature_range=(0, 1))
    yscl = MinMaxScaler(feature_range=(0, 1))
    predxscl = MinMaxScaler(feature_range=(0, 1))

    scaler = MinMaxScaler(feature_range=(0, 1))


    predX = np.copy(data[:,0])
    lenx = len(predX)
    for i in range(1, adv+3):
        predX = np.append(predX, np.array(lenx+i))

    predX = create_dataX(predX)

    """separate X and Y data"""
    trainX, trainY = create_dataset(data, 1)

    """normalize data"""
    trainY = np.reshape(trainY, (-1, 1))
    trainX = xscl.fit_transform(trainX)
    trainY = yscl.fit_transform(trainY)
    predX = predxscl.fit_transform(predX)

    """reshape X data from (samples, features) to (sample, lookback, features)"""
    trainX = np.reshape(trainX, (trainX.shape[0], 1, trainX.shape[1]))
    predX = np.reshape(predX, (predX.shape[0], 1, predX.shape[1]))

    data = scaler.fit_transform(data)

    """LSTM Recurrent Neural Network Model for future data interpolative predictions"""
    model = Sequential()
    model.add(LSTM(4, input_shape=(1, 1)))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    model.fit(trainX, trainY, epochs=100, batch_size=1, verbose=2)

    """Predict and de-normalize data"""
    trainPredict = model.predict(trainX)

    trainPredict = yscl.inverse_transform(trainPredict)
    trainY = yscl.inverse_transform(trainY)

    testpred = model.predict(predX)

    predicted = [list(i)[0]*mx for i in list(testpred)]
    xvals = range(0, len(testpred)

    return [xvals, predicted]


    #output = pd.DataFrame({"Y" : [list(i)[0]*mx for i in list(testpred)]})

    #output.insert(0, "X", range(0, len(testpred)))

    #output.to_csv("output.csv", index=False, float_format="%.0f")


def predict_data(dates, cases, adv):

    df = pd.DataFrame({"Date" : dates, "Cases" : cases})

    df = df.drop("Date", axis=1)

    df.insert(0, "Case ID", range(0, len(df)))

    mx = df["Cases"].max()

    data = df.values

    return do_code(data, adv, mx)
