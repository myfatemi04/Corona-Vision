import json_extractor
import upload, time, requests
from bs4 import BeautifulSoup

lastDatapointsUpdate = 0
name = "Australia"

def import_data():
    global lastDatapointsUpdate

    url = "https://www.health.gov.au/news/health-alerts/novel-coronavirus-2019-ncov-health-alert/coronavirus-covid-19-current-situation-and-case-numbers"
    soup = BeautifulSoup(requests.get(url, timeout=10).text, "html.parser")
    tbody = soup.find("tbody")
    rows = tbody.findAll("tr")
    datapoints = []
    for row in rows:
        tds = row.findAll("td")
        if tds:
            province, number = tds
            province, number = province.text.strip(), number.text.strip().replace(",", "")
            number = int(number)
            if "total" not in province.lower(): 
                datapoints.append({
                    "country": "Australia",
                    "province": province,
                    "total": number
                })
    
    if upload.upload_datapoints(datapoints):
        lastDatapointsUpdate = time.time()

if __name__ == "__main__":
    import_data()