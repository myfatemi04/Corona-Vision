import requests
import upload
import time
from data_sources import minWait

lastDatapointsUpdate = 0
name = "Spain"

def import_data():
    global lastDatapointsUpdate
    if time.time() - lastDatapointsUpdate < minWait:
        print(f"Not uploading {name} because elapsed < minWait")
        return
    else:
        print(f"Loading from {name}...")

    rq = requests.get("https://covid19.isciii.es/resources/ccaa.csv")
    datapoints = []
    for row in rq.text.split("\n")[1:]:
        if row.strip():
            split = row.split(",")
            datapoints.append({
                "country": "Spain",
                "province": split[0],
                "total": int(split[1])
            })
    
    if upload.upload_datapoints(datapoints, "https://covid19.isciii.es/"):
        lastDatapointsUpdate = time.time()

if __name__ == "__main__":
    import_data()