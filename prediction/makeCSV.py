from corona_sql import Session, Datapoint, Location, timeSeriesAll, getLocationObject
import sys
import pandas as pd
import numpy as np

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

    data = {
        "entry_date": X,
        "cases/mil": dfColumn(Y, "total") / population,
        "cases/mil/day": dfColumn(Y, "dtotal") / population
    }

    df = pd.DataFrame(data)

    return df

def timeSeriesDF2(country, province, county):
    X, Y = timeSeriesAll(country, province, county)
    locationObject = getLocationObject(country, province, county)

    if not locationObject:
        sys.stderr.write("Couldn't find that location, sorry!")
        return None

    population = locationObject.population
    populationDensity = locationObject.population_density

    if not population:
        population = float(input("Couldn't find population data. What is it, in thousands of people? "))

    if not populationDensity:
        populationDensity = float(input("Couldn't find population density. What is it, in thousands of people/km^2? "))

    data = {
        "entry_date": X,
        "cases/mil": dfColumn(Y, "total") / population,
        "cases/mil/day": dfColumn(Y, "dtotal") / population,
        "population_density": np.full((len(X),), populationDensity)
    }

    df = pd.DataFrame(data)

    return df
    '''
    socialDistacingTimeSeries = getSocialDistancingTimeSeries(country, province, country)

    X = rows [ % daily change for past 10 days, social distancing past 10 days ]
    Y = rows [ % daily change for next 10 days ]

    model:
    % daily change scaled by MinMaxScaler
    social distancing data from ESRI

    1. Input(20)
        Sigmoid
    2. Dense(20)
        Sigmoid
    3. Dense(20)
        Sigmoid
    4. Dense(10)
        Sigmoid
    5. Dense(5)
        Sigmoid
    6. Dense(5)
        Relu

    First make the model
    Then collect the data
    '''

def getFrame(timeSeriesDF, index, lookahead=10, lookbehind=10):
    before = timeSeriesDF.iloc[index - lookbehind: index]
    row = timeSeriesDF.iloc[index]
    after = timeSeriesDF.iloc[index + 1: index + lookahead + 1]
    x = np.array([*before['cases/mil'], row['cases/mil']])
    y = np.array(after['cases/mil'])
    return x, y

def getFrames(timeSeriesDF, lookahead=10, lookbehind=10):
    X = []
    Y = []
    for frame in range(lookbehind, len(timeSeriesDF) - lookahead):
        frameX, frameY = getFrame(timeSeriesDF, frame, lookahead, lookbehind)
        X.append(frameX)
        Y.append(frameY)
    
    return X, Y