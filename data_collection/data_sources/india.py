import requests
import json_extractor
import upload
import time
from data_sources import minWait
from bs4 import BeautifulSoup

lastDatapointsUpdate = 0

def import_data():
    global lastDatapointsUpdate

    url = "https://www.mohfw.gov.in/"
    soup = BeautifulSoup(requests.get(url, timeout=10).text, "html.parser")
    body = soup.select_one("#state-data tbody")
    rows = body.select("tr")

    datapoints = []
    for row in rows:
        if "total" in row.text.lower():
            continue
        stats = row.select("td")

        print(stats)

        if len(stats) < 5:
            continue
        
        _rank = stats[0].text
        province = stats[1].text
        total = stats[2].text
        recovered = stats[3].text
        deaths = stats[4].text
        
        datapoints.append({
            "country": "India",
            "province": province,
            "total": int(total),
            "recovered": int(recovered),
            "deaths": int(deaths)
        })

    if upload.upload_datapoints(datapoints):
        lastDatapointsUpdate = time.time()