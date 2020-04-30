from . import minWait
from standards import china_provinces

name = "China"

def import_data():
    import requests
    rawURL = "https://raw.githubusercontent.com/canghailan/Wuhan-2019-nCoV/master/Wuhan-2019-nCoV.csv"
    sourceURL = "https://github.com/canghailan/Wuhan-2019-nCoV"

    for row in requests.get(rawURL).text.split("\n")[1:]:
        date, country, countryCode, province, provinceCode, city, cityCode, confirmed, suspected, cured, dead = row.split(",")
        if countryCode == 'CN':
            provinceEng = china_provinces[province]
            print(date, "China", provinceEng, confirmed)
    