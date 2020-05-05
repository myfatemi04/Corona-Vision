import requests
from bs4 import BeautifulSoup
import upload

def import_data():
    url = "https://www.mspbs.gov.py/covid-19.php"
    soup = BeautifulSoup(requests.get(url, verify=False, timeout=10).text, "html.parser")
    print(soup)
    stats = soup.select("font > font")
    datapoint = {
        "country": "Paraguay",
        "total": int(stats[0].text.strip()),
        "deaths": int(stats[1].text.strip()),
        "recovered": int(stats[2].text.strip())
    }

    upload.upload_datapoints([datapoint])