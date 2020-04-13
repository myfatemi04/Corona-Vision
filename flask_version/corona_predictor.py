import math
import numpy as np
import sys
import datetime
import json

import scipy.optimize

def logistic(t, MAX, T_INF, T_RISE):
    return MAX / (1 + np.exp(-(t - T_INF)/T_RISE))

if __name__ == "__main__":
    dates = []
    d = {}

    for date_ in sys.argv[1].split():
        year, month, day = date_.split('-')
        dates.append(datetime.date(int(year), int(month), int(day)))

    if not dates:
        print("data=" + json.dumps({"MAX": 0, "T_INF": 0, "T_RISE": 1, "x": [], "y": []}))
        exit()
    
    min_date = dates[0]

    X = np.array([(date_ - min_date).days for date_ in dates])
    Y = np.array([float(y) for y in sys.argv[2].split()])

    #               a       b   c               c/(1+ae^(-bx))
    bounds = (
        [
            max(Y), # top of regression must be at least the highest date seen
            0,      # the time of the inflection must be at least the starting date
            1       # the time to rise must be at least 1 day (to avoid exponential overflow)
        ],
        [
            7.3e9, # upper bound for MAX
            800,  # upper bound for T_INF
            800  # upper bound for T_RISE
        ]
    )

    # starting values
    p0 = np.clip(
        np.array([
            max(Y),           # max (default: max)
            X[len(X)//2],     # t_inf (default: middle value)
            30,                # t_rise (default: 30 days)
        ]),
        0, 7.3e9  # min and max values
    )

    try:
        (MAX, T_INF, T_RISE), cov = scipy.optimize.curve_fit(logistic, X, Y, p0=p0, maxfev=10000, bounds=bounds)
    except Exception as e:
        MAX, T_INF, T_RISE = list(p0)

    d['MAX'] = MAX
    d['T_INF'] = T_INF
    d['T_RISE'] = T_RISE

    # d = {"MAX": MAX, "T_INF": T_INF, "T_RISE": T_RISE}
    print("data=" + json.dumps(d))
    
