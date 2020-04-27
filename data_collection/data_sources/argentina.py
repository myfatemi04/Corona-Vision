import requests
import json_extractor
import upload
import time
from bs4 import BeautifulSoup
from import_gis import import_gis
from data_sources import minWait

lastDatapointsUpdate = 0

def import_data():
    from datetime import datetime, timedelta

    global lastDatapointsUpdate
    if time.time() - lastDatapointsUpdate < minWait:
        print("Not uploading Argentina because elapsed < minWait")
        return
    else:
        print("Loading from Argentina...")

    # use argentina date
    # ar_time = datetime.now() + timedelta(hours=-3)

    # urlv = ar_time.strftime("https://www.argentina.gob.ar/sites/default/files/%d-%m-%y-reporte-vespertino-covid-19.pdf")
    # urlm = ar_time.strftime("https://www.argentina.gob.ar/sites/default/files/%d-%m-%y-reporte-matutino-covid-19.pdf")
        
    # if upload.upload(result):
    #     lastDatapointsUpdate = time.time()

if __name__ == "__main__":
    import_data()