import requests
import upload
import time
import datetime
from data_sources import minWait

lastDatapointsUpdate = 0

# Massachusetts data - from a ZIP file containing raw data.
def import_data():
    import calendar
    import io
    import zipfile
    global lastDatapointsUpdate

    now = datetime.datetime.now()
    month = calendar.month_name[now.month].lower()
    day = 2#now.day
    year = now.year

    queryURL = f"https://www.mass.gov/doc/covid-19-raw-data-{month}-{day}-{year}/download"
    sourceURL = "https://www.mass.gov/info-details/covid-19-response-reporting#covid-19-cases-in-massachusetts-"

    response = requests.get(queryURL)
    print(queryURL)

    bytesio = io.BytesIO(response.content)
    open("test.zip", "wb").write()

    myzip = zipfile.ZipFile(bytesio)
    counties = myzip.open("County.csv").read()
    testing = myzip.open("Testing2.csv").read()
    print(counties)
    print(testing)

    # if upload.upload(result):
    #     lastDatapointsUpdate = time.time()

if __name__ == "__main__":
    import_data()