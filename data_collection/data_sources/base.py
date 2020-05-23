import requests
from data_sources import source

@source('live', 'NAME')
def import_data():

    # if upload.upload(result):
    #     lastDatapointsUpdate = time.time()

if __name__ == "__main__":
    import_data()