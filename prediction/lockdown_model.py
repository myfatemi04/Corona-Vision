from tensorflow.keras.layers import Dense, LSTM, Dropout
from tensorflow.keras import Sequential
from tensorflow.keras import optimizers
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import makeCSV
import better_predictor
import numpy as np
from matplotlib import pyplot as plt
from corona_sql import Location, Session

# data = makeCSV.timeSeriesDF("United States", "", "")
# results = better_predictor.predict_better(data['day%'], 5)
# plt.plot(results, 'g')
# plt.plot(data['day%'], 'bo')
# plt.show()
def getOptimizer():
    lrSchedule = optimizers.schedules.InverseTimeDecay(
        0.001,
        decay_steps=1000,
        decay_rate=1,
        staircase=False
    )
    return optimizers.Adam(lrSchedule)

def getModel():
    model = Sequential()
    model.add(LSTM(4, activation="sigmoid", input_shape=(1, 5)))
    model.add(Dense(1, activation="linear"))

    # model.compile(optimizer=getOptimizer(), loss="mse")
    model.compile(optimizer="adam", loss="mae")
    return model

class LockdownTrainer:
    def __init__(self):
        self.model = getModel()
        self.X = self.Y = None
    
    def addCountryData(self, country, province, county):
        data = makeCSV.timeSeriesDF(country, province, county)
        if len(data) < 28:
            return
        X, Y = makeCSV.getFrames(data)
        if self.X is None:
            self.X = X
        else:
            self.X = np.concatenate((self.X, X), axis=0)
        if self.Y is None:
            self.Y = Y
        else:
            self.Y = np.concatenate((self.Y, Y), axis=0)

    def fitScaler(self):
        self.Xscaler = MinMaxScaler(feature_range=(0, 1))
        self.Yscaler = MinMaxScaler(feature_range=(0, 1))
        self.X = self.Xscaler.fit_transform(self.X)
        self.Y = self.Yscaler.fit_transform(self.Y)

    def train(self):
        Xtrain, Xtest, Ytrain, Ytest = train_test_split(self.X, self.Y, train_size=0.9)

        Xtrain = Xtrain.reshape(Xtrain.shape[0], 1, Xtrain.shape[1])
        Xtest = Xtest.reshape(Xtest.shape[0], 1, Xtest.shape[1])

        self.model.fit(Xtrain, Ytrain, epochs=5000, batch_size=100, validation_data=(Xtest, Ytest))
        self.model.evaluate(Xtest, Ytest)

        predictions = self.model.predict(Xtest)
        for inp, actual, pred in zip(Xtest, Ytest, predictions):
            print(self.Yscaler.inverse_transform([actual]), self.Yscaler.inverse_transform([pred]))

ldt = LockdownTrainer()
sess = Session()
locations = sess.query(Location.country, Location.province, Location.county).filter(
    Location.population != None,
    Location.population_density != None).all()
sess.close()
import random
for loc in random.sample(locations, 10):
    print("Adding country", *loc)
    ldt.addCountryData(*loc)
# ldt.addCountryData("China", "", "")
# ldt.addCountryData("Japan", "", "")
# ldt.addCountryData("South Korea", "", "")
# ldt.addCountryData("United States", "", "")
# ldt.addCountryData("Italy", "", "")
# ldt.addCountryData("France", "", "")
# ldt.addCountryData("Argentina", "", "")
# ldt.addCountryData("Russia", "", "")
# ldt.addCountryData("Brazil", "", "")
# ldt.addCountryData("Canada", "", "")
# ldt.addCountryData("United Kingdom", "", "")
# ldt.addCountryData("", "", "")

ldt.fitScaler()
ldt.train()