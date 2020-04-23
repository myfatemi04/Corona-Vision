from tensorflow.keras.layers import Dense, LSTM, Dropout
from tensorflow.keras import Sequential
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
def getModel():
    model = Sequential()
    model.add(LSTM(20, activation="tanh", input_shape=(1, 11)))
    model.add(Dropout(0.2))
    model.add(Dense(10, activation="tanh"))

    model.compile(optimizer="adam", loss="mean_absolute_error")
    return model

def predict():
    model = getModel()

    data = makeCSV.timeSeriesDF("United States", "", "")
    X, Y = makeCSV.getFrames(data['day%'])

    scaler = MinMaxScaler()
    X = scaler.fit_transform(X)

    print(X)
    print(Y)
    Xtrain, Xtest, Ytrain, Ytest = train_test_split(X, Y, train_size=0.75)

    Xtrain = Xtrain.reshape(Xtrain.shape[0], 1, Xtrain.shape[1])
    Xtest = Xtest.reshape(Xtest.shape[0], 1, Xtest.shape[1])

    model.fit(Xtrain, Ytrain, epochs=500, batch_size=10)
    model.evaluate(Xtest, Ytest)

    predictions = model.predict(Xtest)
    for pred in predictions:
        print(pred)

predict()