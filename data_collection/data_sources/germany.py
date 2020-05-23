import requests
from bs4 import BeautifulSoup
from data_sources import source

@source('live', name='Germany')
def import_data():
    sourceLink = 'https://www.zeit.de/wissen/gesundheit/coronavirus-echtzeit-karte-deutschland-landkreise-infektionen-ausbreitung#karte'
    jsonURL = 'https://interactive.zeit.de/cronjobs/2020/corona/germany.json'

    jsonContent = requests.get(jsonURL, timeout=10).json()
    datapoints = []
    for state in jsonContent['states']['items']:
        stateStats = state['currentStats']
        yield {
            "country": "Germany",
            "province": state['name'],
            "total": stateStats['count'],
            "deaths": stateStats['dead'],
            "recovered": stateStats['recovered']
        }
        
if __name__ == "__main__":
    import_data()