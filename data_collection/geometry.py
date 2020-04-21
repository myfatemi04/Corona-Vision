def compress_string(string):
    new_string = []
    for x, y in string:
        if len(new_string) < 3:
            new_string.append([x, y])
        else:
            last_x, last_y = new_string[-1]
            former_x, former_y = new_string[-2]
            # if it's the same point, we just skip
            if last_x == x and last_y == y:
                continue
            # if 3 X values in a row are the same, we just change the most recent Y
            if former_x == last_x and last_x == x:
                new_string[-1] = [last_x, y]
            # if 3 Y values in a row are the same, we just change the most recent X
            if former_y == last_y and last_y == y:
                new_string[-1] = [x, last_y]
    return new_string

def compress_poly(poly):
    return [compress_string(string) for string in poly]

def compress_multipoly(multipoly):
    return [compress_poly(poly) for poly in multipoly]

def compress_geo(geo):
    # import json
    if geo['type'] == "Point":
        return geo

    if geo['type'] == "Multipoint":
        return geo

    if geo['type'] == "LineString":
        new_geo = compress_string(geo['coordinates'])

    if geo['type'] == "MultiLineString":
        new_geo = compress_poly(geo['coordinates'])

    if geo['type'] == "Polygon":
        new_geo = compress_poly(geo['coordinates'])

    if geo['type'] == "MultiPolygon":
        new_geo = compress_multipoly(geo['coordinates'])

    if geo['type'] == "GeometryCollection":
        return {'type': "GeometryCollection", "geometries": [compress_geo(geometry) for geometry in geo['geometries']]}

    # print(len(json.dumps(geo)), len(json.dumps(new_geo)))
    
    return {'type': geo['type'], 'coordinates': new_geo}

def get_poly_center(coordinates):
    main_string = coordinates[0]
    return get_string_center(main_string)

def get_string_center(coordinates):
    sum_long = 0
    sum_lat = 0
    if len(coordinates) == 0:
        return None, None
    else:
        for coordinate in coordinates:
            lng, lat = coordinate
            sum_long += lng
            sum_lat += lat
        return sum_long/len(coordinates), sum_lat/len(coordinates)

def get_center_long_lat(geo):
    if geo['type'] == 'Point':
        return geo['coordinates']
    elif geo['type'] == 'Polygon':
        return get_poly_center(geo['coordinates'])
    elif geo['type'] == 'MultiPolygon':
        return get_poly_center(geo['coordinates'][0])

def generate_point_geometry(lng, lat):
    import json
    return json.dumps(
        {"type": "Point", "coordinates": [lng, lat]}
    )

def get_precision(lng, lat):
    import decimal
    lng_d = decimal.Decimal(str(lng))
    lat_d = decimal.Decimal(str(lat))
    lng_precision = -lng_d.as_tuple().exponent
    lat_precision = -lat_d.as_tuple().exponent
    return min(lat_precision, lng_precision)