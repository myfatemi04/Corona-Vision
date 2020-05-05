import requests
import upload
import time
from bs4 import BeautifulSoup
from data_sources import minWait

lastDatapointsUpdate = 0

def import_data():
    global lastDatapointsUpdate

    url = "https://onemocneni-aktualne.mzcr.cz/covid-19"
    soup = BeautifulSoup(requests.get(url, timeout=10).text, "html.parser")
    datapoint = {
        'country': 'Czechia',
        'tests': int(soup.select_one("#count-test").text.replace(" ", "")),
        'total': int(soup.select_one("#count-sick").text.replace(" ", "")),
        'recovered': int(soup.select_one("#count-recover").text.replace(" ", "")),
        'deaths': int(soup.select_one("#count-dead").text.replace(" ", "")),
    }
    
    if upload.upload_datapoints([datapoint]):
        lastDatapointsUpdate = time.time()

if __name__ == "__main__":
    import_data()