import requests
import upload
import time
from data_sources import minWait

lastDatapointsUpdate = 0

def import_data():
    global lastDatapointsUpdate

    queryURL = "https://www.vdh.virginia.gov/content/uploads/sites/182/2020/03/VDH-COVID-19-PublicUseDataset-Cases.csv"
    sourceURL = "http://vdh.virginia.gov/coronavirus/"

    txt = requests.get(queryURL).text
    

    # if upload.upload(result):
    #     lastDatapointsUpdate = time.time()

if __name__ == "__main__":
    import_data()