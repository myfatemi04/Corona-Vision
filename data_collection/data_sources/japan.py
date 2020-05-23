import requests
from data_sources import source

@source('live', name='Japan')
def import_data():
    datapoints = []
    j = requests.get("https://data.covid19japan.com/summary/latest.json", timeout=10).json()
    for row in j['prefectures']:
        yield {
            "country": "Japan",
            "province": row['name'],
            "total": row['confirmed'],
            "deaths": row['deaths'],
            "recovered": row['recovered']
        }
    
