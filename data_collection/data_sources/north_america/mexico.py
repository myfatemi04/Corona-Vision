import requests, json

def import_data():
    source = "https://covid19.sinave.gob.mx/Log.aspx/Grafica22"
    headers = {
        'Content-Type': 'application/json; charset=UTF-8'
    }
    
    # json={} is important because it signals to the server that we want JSON data
    rq = requests.post(source, json={}, timeout=10)
    
    data_string = rq.json()['d']
    data = json.loads(data_string)

    for row in data:
        # data is formatted like this:
        # [ Rank, Province, (Unknown), (State ID?), Positive cases, Negative cases, Suspected cases, Deaths, (Empty), (Unknown) ]
        rank, province, _, _, positive, negative, suspected, deaths, _, _ = row
        if province != 'NACIONAL':
            yield {
                'country': 'Mexico',
                'province': province,
                'total': positive,
                'tests': int(positive) + int(negative),
                'deaths': deaths
            }