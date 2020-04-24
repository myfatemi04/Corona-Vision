from corona_sql import Session, Datapoint, Location, timeSeriesAll, getLocationObject
import sys
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

def dfColumn(objects, attr):
    return np.array([getattr(obj, attr) for obj in objects])

def timeSeriesDF(country, province, county):
    X, Y = timeSeriesAll(country, province, county)
    locationObject = getLocationObject(country, province, county)

    if not locationObject:
        sys.stderr.write("Couldn't find that location, sorry!")
        return None

    population = locationObject.population / 1000
    populationDensity = locationObject.population_density

    if not population:
        population = float(input("Couldn't find population data. What is it, in millions of people? "))

    if not populationDensity:
        populationDensity = float(input("Couldn't find population density. What is it, in thousands of people/km^2? "))

    dailyPercentage = dfColumn(Y, "dtotal") / dfColumn(Y, "total")

    data = {
        "entry_date": X,
        "cases/mil": dfColumn(Y, "total") / population,
        "cases/mil/day": dfColumn(Y, "dtotal") / population,
        "day%": dailyPercentage,
        "popdensity": np.full((len(X),), populationDensity)
    }

    df = pd.DataFrame(data)

    return df

def getFrame(series, index, lookahead=1, lookbehind=10):
    before = series[index - lookbehind + 1: index]
    row = [series[index]]
    after = series[index + 1: index + lookahead + 1]

    x = np.concatenate((before, row), axis=0)
    y = np.array(after)
    return x, y

def getFrames(series, lookahead=1, lookbehind=10):
    X = []
    Y = []
    for frame in range(lookbehind, len(series) - lookahead):
        frameX, frameY = getFrame(series, frame, lookahead, lookbehind)
        X.append(frameX)
        Y.append(frameY)
    
    return np.array(X), np.array(Y)
