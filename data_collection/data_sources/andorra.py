import requests
import json_extractor
import upload
import time
from bs4 import BeautifulSoup
from import_gis import import_gis
from data_sources import minWait

lastDatapointsUpdate = 0

def import_data():
    global lastDatapointsUpdate
    
    url = "https://www.govern.ad/covid/taula.php"

    soup = BeautifulSoup(requests.get(url).text, "html.parser")
    print(soup)
    print(soup.findAll(".col-12"))

    # if upload.upload_datapoints([datapoint]):
    #     lastDatapointsUpdate = time.time()

if __name__ == "__main__":
    import_data()