import requests
import json_extractor
import upload
import time
from bs4 import BeautifulSoup
from import_gis import import_gis
from data_sources import minWait

lastDatapointsUpdate = 0
name = "Australia"

def import_data():
    global lastDatapointsUpdate
    if time.time() - lastDatapointsUpdate < minWait:
        print(f"Not uploading {name} because elapsed < minWait")
        return
    else:
        print(f"Loading from {name}...")

    # if upload.upload(result):
    #     lastDatapointsUpdate = time.time()

if __name__ == "__main__":
    import_data()