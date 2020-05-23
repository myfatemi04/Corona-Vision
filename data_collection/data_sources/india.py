import requests
from data_sources import source
from bs4 import BeautifulSoup

@source('live', name='India')
def import_data():
    
    url = "https://www.mohfw.gov.in/"
    soup = BeautifulSoup(requests.get(url, timeout=10).text, "html.parser")
    body = soup.select_one("#state-data tbody")
    rows = body.select("tr")

    datapoints = []
    for row in rows:
        if "total" in row.text.lower():
            continue
        stats = row.select("td")

        if len(stats) < 5:
            continue
        
        _rank = stats[0].text
        province = stats[1].text
        total = stats[2].text
        recovered = stats[3].text
        deaths = stats[4].text
        
        yield {
            "country": "India",
            "province": province,
            "total": total,
            "recovered": recovered,
            "deaths": deaths
        }

