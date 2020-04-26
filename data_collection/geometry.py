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

def get_precision(lng, lat):
    import decimal
    lng_d = decimal.Decimal(str(lng))
    lat_d = decimal.Decimal(str(lat))
    lng_precision = -lng_d.as_tuple().exponent
    lat_precision = -lat_d.as_tuple().exponent
    return min(lat_precision, lng_precision)