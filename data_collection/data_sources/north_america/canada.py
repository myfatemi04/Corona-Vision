import requests
import datetime
from bs4 import BeautifulSoup
from data_sources import source

@source('live', name='Canada')
def import_data():
    for result in import_news():
        yield result

    for result in import_gov():
        yield result

def import_news():
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
            recovered = data.get('recoveries', None)
            deaths = data.get('deaths', None)
            tests = data.get('totalTests', None)
            yield {
                "entry_date": entryDate,
                "country": "Canada",
                "province": province,
                "total": total,
                "recovered": recovered,
                "deaths": deaths,
                "tests": tests
            }

def import_gov():
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
            yield {
                'country': "Canada",
                'province': province,
                'total': total,
                'deaths': deaths
            }

if __name__ == "__main__":
    import_data()