from tensorflow.keras.layers import Dense, LSTM, Dropout
from tensorflow.keras import Sequential
from tensorflow.keras.optimizers.schedules import InverseTimeDecay
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import makeCSV
import better_predictor
import numpy as np
from matplotlib import pyplot as plt

# data = makeCSV.timeSeriesDF("United States", "", "")
# results = better_predictor.predict_better(data['day%'], 5)
# plt.plot(results, 'g')
# plt.plot(data['day%'], 'bo')
# plt.show()
def getOptimizer():
    lrSchedule = InverseTimeDecay(
        0.001,
        decay_steps=1000,
        decay_rate=1,
        staircase=False
    )
    return Adam(lrSchedule)

def getModel():
    model = Sequential()
    model.add(LSTM(4, activation="tanh", input_shape=(1, 4)))
    model.add(Dense(1, activation="sigmoid"))
    model.add(Dense(1, activation="linear"))

    model.compile(optimizer="adam", loss="mse")
    return model

def predict():
    model = getModel()

    data = makeCSV.timeSeriesDF("South Korea", "", "")

    # data columns are-
    X, Y = makeCSV.getFrames(data['cases/mil/day'])
    Xscaler = MinMaxScaler(feature_range=(0, 1))
    Yscaler = MinMaxScaler(feature_range=(0, 1))
    X = Xscaler.fit_transform(X)
    Y = Yscaler.fit_transform(Y)

    Xtrain, Xtest, Ytrain, Ytest = train_test_split(X, Y, train_size=0.75)

    Xtrain = Xtrain.reshape(Xtrain.shape[0], 1, Xtrain.shape[1])
    Xtest = Xtest.reshape(Xtest.shape[0], 1, Xtest.shape[1])

    model.fit(Xtrain, Ytrain, epochs=1000, batch_size=20, validation_data=(Xtest, Ytest))
    model.evaluate(Xtest, Ytest)

    predictions = model.predict(Xtest)
    for inp, actual, pred in zip(Xtest, Ytest, predictions):
        print(Xscaler.inverse_transform(inp), Yscaler.inverse_transform([actual]), Yscaler.inverse_transform([pred]))

predict()