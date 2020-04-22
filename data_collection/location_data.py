country_codes = {}
admin1_codes = {}
county_codes = {}

country_names = {}
admin1_names = {}
county_names = {}

def store_codes(a0, a1, a2, a0_c, a1_c, a2_c):
    if a0_c:
        country_codes[a0] = a0_c
        country_names[a0_c] = a0

    if a1_c:
        if a0 not in admin1_codes:
            admin1_codes[a0] = {}
        admin1_codes[a0][a1] = a1_c

        if a0 not in admin1_names:
            admin1_names[a0] = {}
        admin1_names[a0][a1_c] = a1

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

# returns country_code, admin1_code, county_code
def get_codes(country, admin1, county):
    country_code = admin1_code = county_code = ''
    
    if country in country_codes:
        country_code = country_codes[country]

    if country in admin1_codes:
        if admin1 in admin1_codes[country]:
            admin1_code = admin1_codes[country][admin1]
            
    if country in county_codes:
        if admin1 in county_codes[country]:
            if county in county_codes[country][admin1]:
                county_code = county_codes[country][admin1][county]
    
    return country_code, admin1_code, county_code

# returns country_code, admin1_code, county_code
def get_country_name(country_code):
    if country_code in country_names:
        return country_names[country_code]

def get_admin1_name(country, admin1_code):
    if country in admin1_names:
        if admin1_code in admin1_names[country]:
            return admin1_names[country][admin1_code]

def get_county_name(country, admin1, county_code):
    if country in county_names:
        if admin1 in county_names[country]:
            if county_code in county_names[country][admin1]:
                return county_names[country][admin1][county_code]

def get_admin_level(country, admin1, county):
    if not country:
        return 'world'
    if not admin1:
        return 'country'
    if not county:
        return 'admin1'
    return 'county'
