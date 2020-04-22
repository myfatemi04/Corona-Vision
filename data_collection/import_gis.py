import re
import json
import json_extractor
import upload
import requests
from defaults import get_defaults

def upload_gis(gis_url, table_labels, use_geometry=True, geometry_precision=6):
    query_url = gis_url + "/query?f=geojson&outFields=*&where=1%3D1"

    if use_geometry == True:
        query_url += "&returnGeometry=true&outSR=4326&geometryPrecision=" + str(geometry_precision)
    else:
        query_url += "&returnGeometry=false"

    source_url = "http://www.arcgis.com/home/webmap/viewer.html?url=" + gis_url
    upload_geojson(source_url=source_url, query_url=query_url, table_labels=table_labels, use_geometry=use_geometry, geometry_precision=3)

def upload_geojson(source_url, query_url, table_labels, use_geometry=True, geometry_precision=3):
    print("Loading GIS data from", source_url)
    content = {}
    content['source_link'] = source_url

    geojson = requests.get(query_url).json()

    defaults = get_defaults()
    for table in table_labels.keys():
        content[table] = []
        labels = {**defaults[table], **table_labels[table]}
        for feature in geojson['features']:
            row = json_extractor.extract_json_row(feature['properties'], labels)

            if use_geometry and table == 'location':
                if feature['geometry']:
                    row['geometry'] = feature['geometry']
                    row['geometry_precision'] = geometry_precision

            content[table].append(row)

    upload.upload(content)

if __name__ == "__main__":
    pass

    #https://opendata.arcgis.com/datasets/628578697fb24d8ea4c32fa0c5ae1843_0.geojson