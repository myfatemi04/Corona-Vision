import requests
import upload
import time
from bs4 import BeautifulSoup
from data_sources import minWait

lastDatapointsUpdate = 0

def import_data():
    global lastDatapointsUpdate

    url = "https://infocovid.ga"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36"
    }

    soup = BeautifulSoup(requests.get(url, headers=headers).text, 'html.parser')
    stats = soup.select(".vc_col-sm-3 > .vc_column-inner")

    tests = int(stats[0].select("p")[1].text)
    total = int(stats[1].select("p")[1].text)
    deaths = int(stats[2].select("p")[1].text)
    recovered = int(stats[3].select("p")[1].text)

    datapoint = {
        "country": "Gabon",
        "tests": tests,
        "total": total,
        "deaths": deaths,
        "recovered": recovered
    }
    
    if upload.upload_datapoints([datapoint]):
        lastDatapointsUpdate = time.time()

if __name__ == "__main__":
    import_data()