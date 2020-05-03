import requests
import upload
import time
from bs4 import BeautifulSoup
from data_sources import minWait

lastDatapointsUpdate = 0
name = "Nigeria"

def import_data():
    global lastDatapointsUpdate

    url = "https://covid19.ncdc.gov.ng/"
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    stats = soup.select(".card-body > h2")
    tests = stats[0].text
    total = stats[1].text
    recovered = stats[3].text
    deaths = stats[4].text
    datapoint = {
        "country": "Nigeria",
        "tests": int(tests.replace(",", "")),
        "total": int(total.replace(",", "")),
        "recovered": int(recovered.replace(",", "")),
        "deaths": int(deaths.replace(",", "")),
    }
    
    if upload.upload_datapoints([datapoint]):
        lastDatapointsUpdate = time.time()

if __name__ == "__main__":
    import_data()