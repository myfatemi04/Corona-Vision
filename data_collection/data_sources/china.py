from standards import state_codes
from data_sources import source

@source('live', name='China')
def import_data():
    import requests
    import datetime
    rawURL = "https://raw.githubusercontent.com/canghailan/Wuhan-2019-nCoV/master/Wuhan-2019-nCoV.csv"
    sourceURL = "https://github.com/canghailan/Wuhan-2019-nCoV"

    for row in requests.get(rawURL, timeout=10).text.split("\n")[1:]:
        if row:
            dateStr, country, countryCode, province, provinceCode, city, cityCode, confirmed, suspected, cured, dead = row.split(",")
            date = datetime.datetime.strptime(dateStr, "%Y-%m-%d").date()
            if province == '':
                if countryCode == 'CN':
                    provinceEng = state_codes['China'][province]
                    yield {
                        "country": "China",
                        "province": provinceEng,
                        "county": cityCode,
                        "total": int(confirmed),
                        "recovered": int(cured),
                        "deaths": int(dead),
                        "entry_date": date
                    }
                # for some reason they switch
                elif country == 'CN':
                    provinceEng = state_codes['China'][provinceCode]
                    yield {
                        "country": "China",
                        "province": provinceEng,
                        "county": city,
                        "total": int(confirmed),
                        "recovered": int(cured),
                        "deaths": int(dead),
                        "entry_date": date
                    }
