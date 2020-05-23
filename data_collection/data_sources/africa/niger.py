import requests
from bs4 import BeautifulSoup
from data_sources import source

@source('live', name='Niger')
def import_data():
    import json

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36"
    }

    url = "https://coronavirus.ne/"
    soup = BeautifulSoup(requests.get(url, headers=headers, timeout=10).text, 'html.parser')
    stats = soup.select(  ".vcex-milestone-time"  )
    total = json.loads(stats[0]['data-options'])['endVal']
    deaths = json.loads(stats[1]['data-options'])['endVal']
    recovered = json.loads(stats[2]['data-options'])['endVal']
    tests = json.loads(stats[4]['data-options'])['endVal']
    
    yield {
        "country": "Niger",
        "total": total,
        "deaths": deaths,
        "recovered": recovered,
        "tests": tests
    }


if __name__ == "__main__":
    import_data()