country_codes = {}
province_codes = {}
county_codes = {}

country_names = {}
province_names = {}
county_names = {}

def store_codes(a0, a1, a2, a0_c, a1_c, a2_c):
    if a0_c:
        country_codes[a0] = a0_c
        country_names[a0_c] = a0

    if a1_c:
        if a0 not in province_codes:
            province_codes[a0] = {}
        province_codes[a0][a1] = a1_c

        if a0 not in province_names:
            province_names[a0] = {}
        province_names[a0][a1_c] = a1

    if a2_c:
        if a0 not in county_codes:
            county_codes[a0] = {}
        if a1 not in county_codes[a0]:
            county_codes[a0][a1] = {}
        county_codes[a0][a1][a2] = a2_c

        if a0 not in county_names:
            county_names[a0] = {}
        if a1 not in county_names[a0]:
            county_names[a0][a1] = {}
        county_names[a0][a1][a2_c] = a2

# returns country_code, province_code, county_code
def get_codes(country, province, county):
    country_code = province_code = county_code = ''
    
    if country in country_codes:
        country_code = country_codes[country]

    if country in province_codes:
        if province in province_codes[country]:
            province_code = province_codes[country][province]
            
    if country in county_codes:
        if province in county_codes[country]:
            if county in county_codes[country][province]:
                county_code = county_codes[country][province][county]
    
    return country_code, province_code, county_code

# returns country_code, province_code, county_code
def get_country_name(country_code):
    if country_code in country_names:
        return country_names[country_code]

def get_province_name(country, province_code):
    if country in province_names:
        if province_code in province_names[country]:
            return province_names[country][province_code]

def get_county_name(country, province, county_code):
    if country in county_names:
        if province in county_names[country]:
            if county_code in county_names[country][province]:
                return county_names[country][province][county_code]

def get_admin_level(country, province, county):
    if not country:
        return 'world'
    if not province:
        return 'country'
    if not county:
        return 'province'
    return 'county'
