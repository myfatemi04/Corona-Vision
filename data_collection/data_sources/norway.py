import requests
from data_sources import source

@source('live', name='Norway')
def import_data():
    url = "https://redutv-api.vg.no/corona/v1/sheets/norway-region-data?exclude=cases"
    json = requests.get(url, timeout=10).json()
    country_data = json['metadata']
    
    yield {
        'country': 'Norway',
        'total': country_data['confirmed']['total'],
        'deaths': country_data['dead']['total']
    }

    

if __name__ == "__main__":
    import_data()