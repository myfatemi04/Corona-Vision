from . import minWait
from standards import china_provinces
import upload

name = "China"

def import_data():
    import requests
    import datetime
    rawURL = "https://raw.githubusercontent.com/canghailan/Wuhan-2019-nCoV/master/Wuhan-2019-nCoV.csv"
    sourceURL = "https://github.com/canghailan/Wuhan-2019-nCoV"

    datapoints = []

    for row in requests.get(rawURL).text.split("\n")[1:]:
        if row:
            dateStr, country, countryCode, province, provinceCode, city, cityCode, confirmed, suspected, cured, dead = row.split(",")
            date = datetime.datetime.strptime(dateStr, "%Y-%m-%d").date()
            if countryCode == 'CN':
                provinceEng = china_provinces[province]
                datapoints.append({
                    "country": "China",
                    "province": provinceEng,
                    "county": cityCode,
                    "total": confirmed,
                    "recovered": cured,
                    "deaths": dead,
                    "entry_date": date
                })
            # for some reason they switch
            elif country == 'CN':
                provinceEng = china_provinces[provinceCode]
                datapoints.append({
                    "country": "China",
                    "province": provinceEng,
                    "county": city,
                    "total": confirmed,
                    "recovered": cured,
                    "deaths": dead,
                    "entry_date": date
                })
    
    upload.upload_datapoints(datapoints, source_link=sourceURL)