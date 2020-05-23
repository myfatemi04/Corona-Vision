import requests
from bs4 import BeautifulSoup
from data_sources import source

# @source('live', name='Australia')
def import_data():
    url = "https://www.health.gov.au/news/health-alerts/novel-coronavirus-2019-ncov-health-alert/coronavirus-covid-19-current-situation-and-case-numbers"
    soup = BeautifulSoup(requests.get(url, timeout=10).text, "html.parser")
    tbody = soup.find("tbody")
    rows = tbody.findAll("tr")
    datapoints = []
    
    for row in rows:
        tds = row.findAll("td")
        if tds:
            province, number = tds
            province, number = province.text.strip(), number.text.strip()
            if "total" not in province.lower(): 
                yield {
                    "country": "Australia",
                    "province": province,
                    "total": number
                }

if __name__ == "__main__":
    import_data()