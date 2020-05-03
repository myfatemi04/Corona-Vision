import requests
import upload
import time
from bs4 import BeautifulSoup
from data_sources import minWait

lastDatapointsUpdate = 0

def import_data():
    global lastDatapointsUpdate

    url = 
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    
    datapoint = {
        "country": ,
    }
    
    if upload.upload_datapoints([datapoint], url):
        lastDatapointsUpdate = time.time()

if __name__ == "__main__":
    import_data()