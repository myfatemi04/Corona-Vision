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

    population = locationObject.population
    populationDensity = locationObject.population_density

    if not population:
        population = float(input("Couldn't find population data. What is it, in millions of people? "))
    else:
        population /= 1000

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

def getFrame(series, index):
    weekAgo3 = sum(series[index - 21:index - 14])
    weekAgo2 = sum(series[index - 14:index - 7])
    weekAgo = sum(series[index - 7:index])
    weekLater = sum(series[index:index + 7])

    x = np.array([weekAgo3, weekAgo2, weekAgo, index])
    y = np.array([weekLater])
    return x, y

def getFrames(series):
    X = []
    Y = []
    for frame in range(21, len(series) - 7):
        frameX, frameY = getFrame(series, frame)
        X.append(frameX)
        Y.append(frameY)
    
    return np.array(X), np.array(Y)
