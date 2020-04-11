# import pandas as pd
# import numpy as np
# from sklearn.preprocessing import MinMaxScaler, LabelEncoder
# from keras.models import Sequential
# from keras.layers import Dense, LSTM
import sys
import math

import scipy.optimize

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
    xvals = [int(x) for x in range(0, len(testpred))]

    return [xvals, predicted]


def predict_data(dates, cases, adv):
    df = pd.DataFrame({"Date" : dates, "Cases" : cases})

    df = df.drop("Date", axis=1)

    df.insert(0, "Case ID", range(0, len(df)))

    mx = df["Cases"].max()

    data = df.values

    return do_code(data, adv, mx)

def logistic(x, numer, b, c):
    return numer/(1 + b * (math.e ** (-c * x)))

print(scipy.optimize.curve_fit(logistic, [1, 2, 3, 4, 5], [2, 4, 8, 16, 32], p0 = [32, 1, 1]))

# if __name__ == "__main__":
#     dates = [int(x) for x in sys.argv[1].split()]
#     cases = [int(x) for x in sys.argv[2].split()]
#     adv = int(sys.argv[3])

#     x, y = predict_data(dates, cases, adv)
#     print(' '.join(str(_) for _ in x))
#     print(' '.join(str(_) for _ in y))
