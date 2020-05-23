import requests
from bs4 import BeautifulSoup

@source('live', 'NAME')
def import_data():
    url = 
    soup = BeautifulSoup(requests.get(url, timeout=10).text, 'html.parser')
    
    yield {
        "country": ,
    }

if __name__ == "__main__":
    import_data()