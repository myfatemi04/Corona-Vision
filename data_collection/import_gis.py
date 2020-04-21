import re
import json
import json_extractor
import upload
import requests
from defaults import get_defaults

def compress_geo(geo):
    if geo['type'] != "Polygon":
        return geo
    new_geo = []
    for poly in geo['coordinates']:
        new_poly = []
        for x, y in poly:
            if len(new_poly) < 3:
                new_poly.append([x, y])
            else:
                last_x, last_y = new_poly[-1]
                former_x, former_y = new_poly[-2]
                # if it's the same point, we just skip
                if last_x == x and last_y == y:
                    continue
                # if 3 X values in a row are the same, we just change the most recent Y
                if former_x == last_x and last_x == x:
                    new_poly[-1] = [last_x, y]
                # if 3 Y values in a row are the same, we just change the most recent X
                if former_y == last_y and last_y == y:
                    new_poly[-1] = [x, last_y]
        new_geo.append(new_poly)
    return {'type': geo['type'], 'coordinates': new_geo}

def upload_gis(gis_url, table_labels, use_geometry=True):
    query_url = gis_url + "/query?f=geojson&outFields=*&where=1%3D1"

    if use_geometry == True:
        query_url += "&returnGeometry=true&outSR=4326&geometryPrecision=3"
    else:
        query_url += "&returnGeometry=false"

    source_url = "http://www.arcgis.com/home/webmap/viewer.html?url=" + gis_url
    upload_geojson(source_url=source_url, query_url=query_url, table_labels=table_labels, use_geometry=use_geometry)

def upload_geojson(source_url, query_url, table_labels, use_geometry=True):
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
                    row['geometry'] = json.dumps(compress_geo(feature['geometry']))

            content[table].append(row)

    upload.upload(content)

if __name__ == "__main__":
    pass

    #https://opendata.arcgis.com/datasets/628578697fb24d8ea4c32fa0c5ae1843_0.geojson