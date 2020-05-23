import requests
import json_extractor
from bs4 import BeautifulSoup
from data_sources import source

@source('live', name='South Korea')
def import_data():
    
    url = "http://ncov.mohw.go.kr/en/bdBoardList.do?brdId=16&brdGubun=162&dataGubun=&ncvContSeq=&contSeq=&board_id="
    soup = BeautifulSoup(requests.get(url, timeout=10).text, "html.parser")
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
        
        yield {
            "country": "South Korea",
            "province": province,
            "total": int(total.replace(",", "")),
            "recovered": int(recovered.replace(",", "")),
            "deaths": int(deaths.replace(",", ""))
        }

