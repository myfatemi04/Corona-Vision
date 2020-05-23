import requests
from data_sources import source

@source('live', name='Albania')
def import_data():

    rq = requests.get('https://coronavirus.al/api/qarqet.php', timeout=10)
    j = rq.json()
    datapoints = []
    locations = []
    
    for row in j:
        yield {
            'country': 'Albania',
            'province': row['qarku'],
            'total': row['raste_gjithsej'],
            'recovered': row['sheruar'],
            'deaths': row['vdekur'],
            'serious': row['terapi_int'],
            'hospitalized': row['mjekim_spitalor'],
            'tests': row['teste']
        }
