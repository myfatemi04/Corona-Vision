import requests

from data_sources import source

@source('live', name='US New Jersey')
def import_data():
    queryURL = "https://services7.arcgis.com/Z0rixLlManVefxqY/arcgis/rest/services/DailyCaseCounts/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&outFields=*"
    sourceURL = "https://www.nj.gov/health/cd/topics/covid2019_dashboard.shtml"

    json = requests.get(queryURL, timeout=10).json()

    for feature in json['features']:
        attr = feature['attributes']
        yield {
            "country": "United States",
            "province": "New Jersey",
            "county": attr['COUNTY'].capitalize(),
            "total": attr['TOTAL_CASES'],
            "deaths": attr['TOTAL_DEATHS'],
        }

if __name__ == "__main__":
    import_data()