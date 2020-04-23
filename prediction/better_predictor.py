import pandas as pd
from numpy import array
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.layers import Conv1D, MaxPooling1D
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
import numpy
import matplotlib.pyplot as plt

def split_sequence(sequence, n_steps):
	X, y = list(), list()
	for i in range(len(sequence)):
		# find the end of this pattern
		end_ix = i + n_steps
		# check if we are beyond the sequence
		if end_ix > len(sequence)-1:
			break
		# gather input and output parts of the pattern
		seq_x, seq_y = sequence[i:end_ix], sequence[end_ix]
		X.append(seq_x)
		y.append(seq_y)
	return array(X), array(y)

# define input sequence

"""
df = pd.read_csv("test_data.csv")
raw = df["Cases"].tolist()
dataframe = pd.DataFrame({"Series" : raw})

dataset = dataframe.values
dataset = dataset.astype('float32')
"""

def predict_better(raw, adv):
    numpy.random.seed(11)
    dataframe = pd.DataFrame({"Series" : raw})

    dataset = dataframe.values
    dataset = dataset.astype('float32')

    scaler = MinMaxScaler(feature_range=(0, 1))
    dataset = scaler.fit_transform(dataset)

    raw_seq = dataset.tolist()

    # choose a number of time steps
    n_steps = 10
    # split into samples
    X, y = split_sequence(raw_seq, n_steps)
    # reshape from [samples, timesteps] into [samples, timesteps, features]
    n_features = 1
    X = X.reshape((X.shape[0], X.shape[1], n_features))
    # define model
    model = Sequential()
    model.add(Conv1D(filters=64, kernel_size=5, activation='relu', input_shape=(n_steps, n_features)))
    model.add(MaxPooling1D(pool_size=5))

    model.add(Flatten())
    model.add(Dense(50, activation='sigmoid'))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    # fit model
    model.fit(X, y, epochs=1000, verbose=2)
    # demonstrate prediction
    y = scaler.inverse_transform(y).tolist()

    look_back = n_steps

    predArr = y[-look_back:]
    predArr = [i[0] for i in predArr]

    trainer = y.copy()

    predicted = []

    for i in range(adv+1):
        temp = numpy.array(predArr.copy())


        temp = numpy.reshape(temp, (look_back, 1))
        temp = scaler.transform(temp)
        temp = numpy.reshape(temp, (1, temp.shape[0], temp.shape[1]))
        predval = scaler.inverse_transform(model.predict(temp, verbose=0)).tolist()[0][0]

        predicted.append(predval)
        # print(predval)
        if i > 0:
            y.append(predval)

        predArr.append(predval)
        predArr = predArr[1:]
    
    return numpy.concatenate((raw[:look_back], [i[0] for i in y if "list" in str(type(i))], predicted), axis=0)

if __name__ == "__main__":
    belarus = "1.0, 1.0, 1.0, 1.0, 1.0, 6.0, 6.0, 6.0, 6.0, 6.0, 6.0, 9.0, 9.0, 12.0, 27.0, 27.0, 27.0, 36.0, 36.0, 51.0, 51.0, 69.0, 76.0, 76.0, 81.0, 81.0, 86.0, 86.0, 94.0, 94.0, 94.0, 152.0, 152.0, 163.0, 304.0, 351.0, 440.0, 562.0, 700.0, 861.0, 1066.0, 1486.0, 1981.0, 2226.0, 2578.0".split(", ")
    belarus = [float(i) for i in belarus]
    pred = train(belarus, adv=len(belarus))
    plt.plot(pred, "g")
    plt.plot(belarus, "bo")
    plt.show()

# trainer = [i[0] for i in trainer if "list" in str(type(i))]
# print(len(y))
# print(len(trainer))

# plt.plot(y+predicted, "bo")
# plt.plot(trainer, "go")
# plt.show()