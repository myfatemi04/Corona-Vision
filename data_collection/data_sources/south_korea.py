import requests
import json_extractor
import upload
import time
from data_sources import minWait
from bs4 import BeautifulSoup

lastDatapointsUpdate = 0

def import_data():
    global lastDatapointsUpdate

    url = "http://ncov.mohw.go.kr/en/bdBoardList.do?brdId=16&brdGubun=162&dataGubun=&ncvContSeq=&contSeq=&board_id="
    soup = BeautifulSoup(requests.get(url).text, "html.parser")
    body = soup.select_one("table.num tbody")
    rows = body.select("tr")

    datapoints = []
    for row in rows:
        if "total" in row.text.lower():
            continue
        stats = row.select("td")

        province = row.select_one("th").text
        total = stats[3].text
        recovered = stats[5].text
        deaths = stats[6].text
        
        datapoints.append({
            "country": "South Korea",
            "province": province,
            "total": int(total.replace(",", "")),
            "recovered": int(recovered.replace(",", "")),
            "deaths": int(deaths.replace(",", ""))
        })

    if upload.upload_datapoints(datapoints):
        lastDatapointsUpdate = time.time()