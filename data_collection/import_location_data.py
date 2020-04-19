import pandas as pd
import json
from corona_sql_new import Session, add_location_data, get_admin1_name

def na(val, sub):
    if pd.isna(val):
        return sub
    return val

def import_countries():
    session = Session()
    country_location_df = pd.read_csv("location_data/country_locations.tsv", sep='\t', keep_default_na=False, na_values=['_'])
    print("Loading country data")
    i = 0
    for _, row in country_location_df.iterrows():
        i += 1
        print(f'\r{i}/{len(country_location_df)}          ', end='\r')
        country_code, lat, lng, country_name = row
        country = {}
        country['latitude'] = lat
        country['longitude'] = lng
        country['admin0_code'] = country_code
        country['admin0'] = country_name
        add_location_data(country, session)
    session.commit()

def import_states():
    session = Session()
    state_location_df = pd.read_csv("location_data/us_state_locations.tsv", sep='\t', keep_default_na=False, na_values=['_'])
    print("Loading US state data")
    i = 0
    for _, row in state_location_df.iterrows():
        i += 1
        print(f'\r{i}/{len(state_location_df)}          ', end='\r')
        state_code, lat, lng, state_name = row
        state = {}
        state['latitude'] = lat or None
        state['longitude'] = lng or None
        state['admin1_code'] = state_code
        state['admin1'] = state_name
        state['admin0'] = 'United States'
        state['admin0_code'] = 'US'
        add_location_data(state, session)
    session.commit()

def import_counties():
    session = Session()
    us_counties = pd.read_csv("location_data/county_locations.txt", sep='|')
    """
    County_Name -> Admin2
    Census_Code -> Admin2_Code
    Primary_Latitude -> Latitude
    Primary_Longitude -> Longitude
    State_Alpha -> Admin1_Code
    state_names[State_Alpha] -> Admin1
    "United States" -> Admin0
    "US" -> Admin0_Code
    """
    i = 0
    seen_counties = set()
    print("Loading county data")
    for _, row in us_counties.iterrows():
        i += 1
        print(f'\r{i}/{len(us_counties)}          ', end='\r')
        county = {}
        # Don't have individual cities as their own county
        if row['COUNTY_NAME'] in seen_counties:
            continue
        seen_counties.add(row['COUNTY_NAME'])
        admin1_name = get_admin1_name("United States", row['STATE_ALPHA'])
        if not admin1_name:
            continue
        if row.isna().values.any() or row.isnull().values.any():
            print("Found NaN row", end='\r')
            continue
        county['admin2'] = row['COUNTY_NAME']
        county['admin2_code'] = row['CENSUS_CODE']
        county['latitude'] = row['PRIMARY_LATITUDE']
        county['longitude'] = row['PRIMARY_LONGITUDE']
        county['admin1'] = admin1_name
        county['admin1_code'] = row['STATE_ALPHA']
        county['admin0'] = "United States"
        county['admin0_code'] = "US"
        skip = False
        for col in county:
            if col not in ['latitude', 'longitude'] and pd.isna(county[col]):
                skip = True
                break
        if not skip:
            add_location_data(county, session)

    session.commit()

def import_population():
    df = pd.read_csv("location_data/Population_Data.csv")
    session = Session()
    print("Loading population data")
    i = 0
    for _, row in df.iterrows():
        i += 1
        print(f"\r{i}/{len(df)}", end='\r')
        if row['Variant'] == 'Medium' and row['Time'] == 2020:
            data = {}
            data['admin0'] = row['Location']
            data['population_density'] = row['PopDensity']
            data['population'] = row['PopTotal']
            add_location_data(data, session, add_new=False)
    session.commit()

def import_all():
    import_countries()
    import_states()
    import_counties()
    import_population()

if __name__ == "__main__":
    import_population()