import requests
import json_extractor
import upload
import time
from bs4 import BeautifulSoup
from import_gis import import_gis
from data_sources import minWait

lastDatapointsUpdate = 0
name = "France"

def import_data():
    global lastDatapointsUpdate
    
    # france_today = datetime.utcnow() + timedelta(hours=2)
    # import_date(france_today)
    import_dashboard()

def import_dashboard():
    global lastDatapointsUpdate

    url = "https://dashboard.covid19.data.gouv.fr/data/code-FRA.json"
    rq = requests.get(url).json()
    latest = rq[-1]
    
    _ = lambda x, y: x[y] if y in x else None

    datapoint = {
        'country': "France",
        "total": latest['casConfirmes'],
        'deaths': latest['deces'] + (_(latest, 'decesEhpad') or 0),
        'serious': latest['reanimation'],
        'hospitalized': latest['hospitalises'],
        'recovered': latest['gueris'],
        'tests': None
    }

    if upload.upload_datapoints([datapoint], "https://dashboard.covid19.data.gouv.fr/"):
        lastDatapointsUpdate = time.time()

def import_historical_data():
    from datetime import datetime
    url = "https://dashboard.covid19.data.gouv.fr/data/code-FRA.json"
    rq = requests.get(url).json()

    datapoints = []

    _ = lambda x, y: x[y] if y in x else None

    for row in rq:
        datapoints.append({
            'country': "France",
            "total": row['casConfirmes'],
            'deaths': row['deces'] + (_(row, 'decesEhpad') or 0),
            'serious': _(row, 'reanimation'),
            'hospitalized': _(row, 'hospitalises'),
            'recovered': _(row, 'gueris'),
            'tests': _(row, 'testsRealises'),
            'entry_date': datetime.strptime(row['date'], "%Y-%m-%d").date()
        })

    print(datapoints)

    upload.upload_datapoints(datapoints, "https://dashboard.covid19.data.gouv.fr/")

def import_date(d):
    global lastDatapointsUpdate
    url = d.strftime("https://dashboard.covid19.data.gouv.fr/data/date-%Y-%m-%d.json")

    datapoints = []
    
    _ = lambda x, y: x[y] if y in x else None

    for row in requests.get(url).json():
        if row['code'].startswith("REG"):
            datapoints.append({
                'country': 'France',
                'province': row['nom'],
                'recovered': row['gueris'],
                'hospitalized': row['hospitalises'],
                'deaths': row['deces'] + (_(row, 'decesEhpad') or 0),
                'entry_date': d
            })

    if upload.upload_datapoints(datapoints, "https://dashboard.covid19.data.gouv.fr/"):
        lastDatapointsUpdate = time.time()

if __name__ == "__main__":
    import_data()