import requests
from data_sources import source

@source('live', name='Spain')
def import_data():
    rq = requests.get("https://covid19.isciii.es/resources/ccaa.csv", timeout=10)
    datapoints = []
    for row in rq.text.split("\n")[1:]:
        if row.strip():
            split = row.split(",")
            yield {
                "country": "Spain",
                "province": split[0],
                "total": int(split[1])
            }


if __name__ == "__main__":
    import_data()