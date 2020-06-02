import requests
import standards
from bs4 import BeautifulSoup
from data_sources import source

def has_class(node, cls):
    return cls in node.attrs.get("class", [])

@source('live', name='Worldometers')
def import_data():
    data = requests.get("http://www.worldometers.info/coronavirus")
    soup = BeautifulSoup(data.text, "html.parser")
    table = soup.find("table", id="main_table_countries_today")

    for row in table.find("tbody").findAll("tr"):
        if row.has_attr("data-continent"):
            continue
        
        columns = row.findAll("td")

        rank = columns[0].text
        name = columns[1].text
        total = columns[2].text
        # dtotal = columns[3].text
        deaths = columns[4].text
        # ddeaths = columns[5].text
        recovered = columns[6].text
        # drecovered = columns[7].text
        active = columns[8].text
        serious = columns[9].text
        # cases_mil = columns[10].text
        # deaths_mil = columns[11].text
        tests = columns[12].text
        # tests_mil = columns[13].text
        # population = columns[14].text
        
        # This country has a data dispute with Worldometers
        if name == "France":
            continue
        
        row = {
            "country": name,
            "total": total,
            "deaths": deaths,
            "recovered": recovered,
            "active": active,
            "serious": serious,
            "tests": tests
        }
        
        yield row

def getSources():
    """
    I created this function to extract which sources Worldometers used for each country.
    That way, I could find more live and state-level data.
    """
    from bs4 import BeautifulSoup
    import datetime, time

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
    