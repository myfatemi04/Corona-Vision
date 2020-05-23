import requests
from datetime import datetime
from bs4 import BeautifulSoup
from data_sources import source

def parse_datapoint(row):
    if row['deces'] == 'NaN':
        row['deces'] = 0
    if row.get('decesEhpad', 0) == 'NaN':
        row['decesEhpad'] = 0
        
    return {
        'country': "France",
        'total': row['casConfirmes'],
        'deaths': int(row['deces']) + int(row.get('decesEhpad', 0)),
        'serious': row.get('reanimation', None),
        'hospitalized': row.get('hospitalises', None),
        'recovered': row.get('gueris', None),
        'tests': row.get('testsRealises', None),
        'entry_date': datetime.strptime(row['date'], "%Y-%m-%d").date()
    }

@source('live', name='France')
def import_dashboard():
    url = "https://dashboard.covid19.data.gouv.fr/data/code-FRA.json"
    rq = requests.get(url, timeout=10).json()
    latest = rq[-1]

    yield parse_datapoint(latest)

@source('historical', name='France')
def import_historical_data():
    from datetime import datetime
    url = "https://dashboard.covid19.data.gouv.fr/data/code-FRA.json"
    rq = requests.get(url, timeout=10).json()

    for row in rq:
        yield parse_datapoint(row)

def import_date(d):
    url = d.strftime("https://dashboard.covid19.data.gouv.fr/data/date-%Y-%m-%d.json")

    datapoints = []
    
    _ = lambda x, y: x[y] if y in x else None

    for row in requests.get(url, timeout=10).json():
        if row['code'].startswith("REG"):
            yield {
                'country': 'France',
                'province': row['nom'],
                'recovered': row['gueris'],
                'hospitalized': row['hospitalises'],
                'deaths': row['deces'] + (_(row, 'decesEhpad') or 0),
                'entry_date': d
            }

