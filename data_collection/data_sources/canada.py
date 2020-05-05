import requests
import json_extractor
import upload
import time
import datetime
from data_sources import minWait
from bs4 import BeautifulSoup

lastDatapointsUpdate = 0
name = "Canada"

def import_data():
    global lastDatapointsUpdate

    import_news()
    import_gov()

def intify(x):
    x = x.replace(",","").strip()
    if not x.isdigit():
        return None
    else:
        return int(x)

def import_news():
    global lastDatapointsUpdate
    import string
    sourceURL = "https://www.ctvnews.ca/health/coronavirus/tracking-every-case-of-covid-19-in-canada-1.4852102"
    jsonURL = "https://stats.ctvnews.ca/covidDapi/getAllCovidData"

    # referer is required for authorization
    headers = {
        "referer": "https://www.ctvnews.ca/health/coronavirus/tracking-every-case-of-covid-19-in-canada-1.4852102"
    }

    datapoints = []
    content = requests.get(jsonURL, headers=headers, timeout=10).json()
    for row in content:
        entryDate = datetime.datetime.strptime(row['date'], "%Y-%m-%d").date()
        provinces = row['data']
        for data in provinces:
            province = string.capwords(data['provinceLabel'])

            total = data['totalCases']
            recovered = data['recoveries'] if 'recoveries' in data else None
            deaths = data['deaths'] if 'deaths' in data else None
            tests = data['totalTests'] if 'totalTests' in data else None
            datapoints.append({
                "entry_date": entryDate,
                "country": "Canada",
                "province": province,
                "total": total,
                "recovered": recovered,
                "deaths": deaths,
                "tests": tests
            })
    
    if upload.upload_datapoints(datapoints):
        lastDatapointsUpdate = time.time()

def import_gov():
    global lastDatapointsUpdate
    url = "https://www.canada.ca/en/public-health/services/diseases/2019-novel-coronavirus-infection.html"
    soup = BeautifulSoup(requests.get(url, timeout=10).text, 'html.parser')
    stats = soup.select("#dataTable tbody tr")
    datapoints = []
    for row in stats:
        tds = row.select("td")
        province = tds[0].text
        total = int(tds[1].text.replace(",", ""))
        deaths = int(tds[3].text.replace(",", ""))
        if province != "Canada":
            datapoints.append({
                'country': "Canada",
                'province': province,
                'total': total,
                'deaths': deaths
            })
    
    if upload.upload_datapoints(datapoints):
        lastDatapointsUpdate = time.time()

if __name__ == "__main__":
    import_data()