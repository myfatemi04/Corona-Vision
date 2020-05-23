import requests
from bs4 import BeautifulSoup
from data_sources import source

@source('live', name='Brazil')
def import_data():
    headers = {
        'x-parse-application-id': 'unAFkcaNDeXajurGB7LChj8SgQYS2ptm'
    }

    jsonURL = "https://xx9p7hp1p7.execute-api.us-east-1.amazonaws.com/prod/PortalMapa"
    sourceURL = "https://covid.saude.gov.br/"

    content = requests.get(jsonURL, headers=headers, timeout=10).json()
    datapoints = []
    locations = []

    for row in content['results']:
        yield {
            "country": "Brazil",
            "province": row['nome'],
            "total": row['qtd_confirmado'],
            "deaths": row['qtd_obito']
        }

if __name__ == "__main__":
    import_data()