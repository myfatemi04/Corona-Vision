import requests
import json_extractor
import upload
import time
from bs4 import BeautifulSoup
from import_gis import import_gis
from data_sources import minWait

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
    url = "https://www.ctvnews.ca/health/coronavirus/tracking-every-case-of-covid-19-in-canada-1.4852102"
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    provinces = soup.select(".covid-province-container")
    datapoints = []
    for province_container in provinces:
        province = province_container.select_one("h2").contents[0].strip()
        tds = lambda x: x.select("tbody")[-1].select("td")
        totals_table = tds(province_container.select_one(".cases-table"))
        active_recovered_deaths_table = tds(province_container.select_one(".status-table"))
        tests_table = tds(province_container.select_one(".results-table"))
        
        datapoint = {
            'country': 'Canada',
            'province': province
        }

        total = intify(totals_table[0].text)
        recovered = intify(active_recovered_deaths_table[1].text)
        deaths = intify(active_recovered_deaths_table[2].text)
        tests = intify(tests_table[0].text)

        if total: datapoint['total'] = total
        if recovered: datapoint['recovered'] = recovered
        if deaths: datapoint['deaths'] = deaths
        if tests: datapoint['tests'] = tests

        datapoints.append(datapoint)
    
    if upload.upload_datapoints(datapoints, url):
        lastDatapointsUpdate = time.time()

def import_gov():
    global lastDatapointsUpdate
    url = "https://www.canada.ca/en/public-health/services/diseases/2019-novel-coronavirus-infection.html"
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
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
    
    if upload.upload_datapoints(datapoints, url):
        lastDatapointsUpdate = time.time()

if __name__ == "__main__":
    import_data()