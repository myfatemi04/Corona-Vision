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
        sys.stderr.write("[{}, {}, {}] Couldn't find that location, sorry!".format(country, province, county))
        return None

    population = locationObject.population
    populationDensity = locationObject.population_density

    if not population:
        population = float(input("Couldn't find {} {} {} population data. What is it, in millions of people? ".format(country, province, county)))
    else:
        population /= 1000

    if not populationDensity:
        populationDensity = float(input("Couldn't find {} {} {} population density. What is it, in thousands of people/km^2? ".format(country, province, county)))

    dailyPercentage = dfColumn(Y, "dtotal") / dfColumn(Y, "total") + 1

    data = {
        "entry_date": X,
        "cases/mil": dfColumn(Y, "total") / population,
        "cases/mil/day": dfColumn(Y, "dtotal") / population,
        "day%": dailyPercentage,
        "popdensity": np.full((len(X),), populationDensity),
        "transit_change": dfColumn(Y, "transit_change")
    }

    df = pd.DataFrame(data)

    return df

def last3Weeks(series, index):
    weekAgo3 = sum(series[index - 21:index - 14])
    weekAgo2 = sum(series[index - 14:index - 7])
    weekAgo = sum(series[index - 7:index])
    weekLater = sum(series[index:index + 7])
    return weekAgo3, weekAgo2, weekAgo, weekLater

def getFrame(df, index):
    weekAgo3, weekAgo2, weekAgo, weekLater = last3Weeks(df['cases/mil/day'], index)
    transit3, transit2, transit1, _ = last3Weeks(df['transit_change'], index)

    x = np.array([weekAgo3, weekAgo2, weekAgo, transit3, transit2, transit1, index, df['popdensity'][index]])
    y = np.array([weekLater])
    return x, y

def getFrames(df):
    X = []
    Y = []
    for frame in range(21, len(df) - 7):
        frameX, frameY = getFrame(df, frame)
        X.append(frameX)
        Y.append(frameY)
    
    return np.array(X), np.array(Y)
