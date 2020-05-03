import requests
import upload
import time
from bs4 import BeautifulSoup
from data_sources import minWait

lastDatapointsUpdate = 0

def import_data():
    global lastDatapointsUpdate

    url = 'https://www.gov.bm/coronavirus'
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    statsTable = soup.select(  "table"  )[1]
    statsRows = statsTable.select("tr")
    tests = int(statsRows[1].select("td")[-1].text)
    total = int(statsRows[3].select("td")[-1].text)
    recovered = int(statsRows[9].select("td")[-1].text)
    deaths = int(statsRows[12].select("td")[-1].text)
    
    datapoint = {
        "country": "Bermuda",
        "tests": tests,
        "total": total,
        "recovered": recovered,
        "deaths": deaths
    }
    
    if upload.upload_datapoints([datapoint], url):
        lastDatapointsUpdate = time.time()

if __name__ == "__main__":
    import_data()