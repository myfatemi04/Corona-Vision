import requests
import standards
from data_parser import import_table
from data_sources import source

minWait = 60

disallowed = [
    "France"    # clear data disputes between the countries
]

@source('live', name='Worldometers')
def import_data():
    results = import_table(
        "http://www.worldometers.info/coronavirus",
        ["#main_table_countries_today", 0],
        {
            "datapoint": {
                "country": ["Country,  Other"],
                "total": ["Total  Cases", "::number"],
                "deaths": ["Total  Deaths", "::number"],
                "serious": ["Serious,  Critical", "::number"],
                "tests": ["Total  Tests", "::number"],
                "recovered": ["Total  Recovered", "::number"]
            }
        }
    )
    
    for result in results['datapoint']:
        result['country'], _, _ = standards.normalize_name(result['country'], '', '')
        if result['country'] not in disallowed:
            yield result

def getSources():
    from bs4 import BeautifulSoup
    import datetime

    textContent = requests.get("http://www.worldometers.info/coronavirus", timeout=10).text
    soup = BeautifulSoup(textContent, "html.parser")

    # select whichever news date is "today"
    firstNews = soup.select_one(time.strftime("#newsdate%Y-%m-%d"))
    
    # find list elements
    elements = firstNews.select("li")

    for elem in elements:
        country = elem.select_one("strong > a")
        newsSource = elem.select_one(".news_source_a")
        if country and newsSource:
            print(country.text, newsSource['href'])
    