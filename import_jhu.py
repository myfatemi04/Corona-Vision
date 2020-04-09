import pandas as pd
import numpy as np
import io
from corona_sql import db, Datapoint, add_or_update
from datetime import timedelta, date
import standards
import web_app
import requests

def add_tuple_values(a, b):
    return tuple(sum(x) for x in zip(a, b))

def add_to_dict(dct, country, province, admin2, value_list):
    
    # use a set so that if for example province = "", we don't add the values to (country, "", "") twice
    combinations = set(
        [
            (country, province, admin2),
            (country, province, ""),
            (country, "", ""),
            ("", "", "")
        ]
    )

    for combination in combinations:
        if combination not in dct:
            dct[combination] = value_list
        else:
            dct[combination] = add_tuple_values(dct[combination], value_list)

    return dct

def import_data(csv_text, entry_date, is_live):
    string_io = io.StringIO(csv_text)
    df = pd.read_csv(string_io)
    yesterday = entry_date + timedelta(days=-1)
    
    lat_col = lng_col = ""
    country_col = province_col = admin2_col = ""
    confirmed_col = death_col = recovered_col = ""
    
    for col in df.columns:
        if 'lat' in col.lower(): lat_col = col
        elif 'long' in col.lower(): lng_col = col
        elif 'country' in col.lower(): country_col = col
        elif 'province' in col.lower(): province_col = col
        elif 'admin2' in col.lower(): admin2_col = col
        elif "death" in col.lower(): death_col = col
        elif "dead" in col.lower(): death_col = col
        elif "confirm" in col.lower(): confirmed_col = col
        elif "recover" in col.lower(): recovered_col = col
    
    data_points = {}
    location_data = {}
    accurate = set()
    primary = set()
        
    for _, row in df.iterrows():
        country = standards.fix_country_name(row[country_col].strip())
        province = admin2 = ''
        
        if not pd.isnull(row[province_col]):
            province = row[province_col].strip()
        
        if admin2_col and not pd.isnull(row[admin2_col]):
            admin2 = row[admin2_col].strip()
        else:
            if ", " in province and country == 'United States':
                comma_index = province.rfind(", ")
                admin2, state_code = province[:comma_index], province[comma_index + 2:]
                if state_code:
                    state_code = state_code.split()[0]
                    province = standards.get_state_name("US", state_code) or state_code
                    if province == 'D.C.':
                        province = "District of Columbia"
        
        primary.add((country, province, admin2))
        
        confirmed = row[confirmed_col]
        deaths = row[death_col]
        recovered = row[recovered_col]

        if np.isnan(confirmed): confirmed = 0
        if np.isnan(deaths): deaths = 0
        if np.isnan(recovered): recovered = 0

        active = confirmed - deaths - recovered

        admin2_region = country, province, admin2
        province_region = country, province, ''
        country_region = country, '', ''

        # save the location data if we can
        if lat_col and lng_col:
            lat, lng = row[lat_col], row[lng_col]
            if not np.isnan(lat) and not np.isnan(lng):
                if lat != 0 or lng != 0:
                    location_data[admin2_region] = lat, lng
                    accurate.add(admin2_region)
        
        province_location = standards.get_state_location(country, province)
        if province_location:
            if province_region not in location_data:
                location_data[province_region] = province_location
                accurate.add(province_region)
            if admin2_region not in location_data:
                location_data[admin2_region] = province_location  # estimate to province location
            
        country_location = standards.get_country_location(country)
        if country_location:
            if country_region not in location_data:
                location_data[country_region] = country_location
                accurate.add(country_region)
            if province_region not in location_data:
                location_data[province_region] = country_location
            if admin2_region not in location_data:
                location_data[admin2_region] = country_location
        
        data_points = add_to_dict(data_points, country, province, admin2, (confirmed, deaths, recovered, active))

    print("\tFinished downloading and processing")
    print("\tUploading...")

    with web_app.app.app_context():
        session = db.session()
        i = 0
        for region, stats in data_points.items():
            country, province, admin2 = region
            confirmed, deaths, recovered, active = stats
            is_primary = region in primary

            active = confirmed - recovered - deaths

            location_labelled = region in location_data
            location_accurate = region in accurate

            if region in location_data:
                lat, lng = location_data[region]
            else:
                lat, lng = 0, 0

            yesterday_data = session.query(Datapoint).filter_by(
                entry_date=yesterday,
                
                admin2=admin2,
                province=province,
                country=country
            ).all()

            yesterday_confirmed = yesterday_recovered = yesterday_deaths = yesterday_active = 0
            is_first_day = True

            if yesterday_data:
                is_first_day = False
                datapoint = yesterday_data[0]

                yesterday_confirmed = datapoint.confirmed
                yesterday_recovered = datapoint.recovered
                yesterday_deaths = datapoint.deaths
                yesterday_active = datapoint.active

            new_data = Datapoint(
                entry_date=entry_date,
                
                admin2=admin2,
                province=province,
                country=country,
                
                latitude=lat,
                longitude=lng,

                location_labelled=location_labelled,
                location_accurate=location_accurate,
                is_first_day=is_first_day,
                is_primary=is_primary,
                
                confirmed=confirmed,
                deaths=deaths,
                recovered=recovered,
                active=active,

                dconfirmed=confirmed-yesterday_confirmed,
                ddeaths=deaths-yesterday_deaths,
                drecovered=recovered-yesterday_recovered,
                dactive=active-yesterday_active
            )

            if i % 500 == 0:
                print("\t" + str(i) + "/" + str(len(data_points)))

            session.add(new_data)

            if admin2 != '' and is_live:
                data_row = {
                    "admin2": admin2, "province": province, "country": country,
                    "confirmed": confirmed, "deaths": deaths, "recovered": recovered, "active": active,
                    "dconfirmed": confirmed-yesterday_confirmed,
                    "ddeaths": deaths-yesterday_deaths,
                    "drecovered": recovered-yesterday_recovered,
                    "dactive": active-yesterday_active,
                    "source_link": "https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports"
                    
                }
                add_or_update(session, data_row, commit=False)

            i += 1
        
        session.commit()
        
        print(f"\tImported data for date {entry_date}")

def download_data_for_date(entry_date):
    with web_app.app.app_context():
        session = db.session()
        existing_data = session.query(Datapoint).filter_by(entry_date=entry_date).first()

        # don't do it again
        if existing_data:
            print("\tData already exists")
            return 'exists'

        date_formatted = entry_date.strftime("%m-%d-%Y")
        github_raw_url = f"https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{date_formatted}.csv"
        response = requests.get(github_raw_url)
        print("Attempting to download " + date_formatted)
        
        if response.status_code != 200:
            print("\tDate not found")
            return '404'
        else:
            csv_text = response.text
            is_live = entry_date >= (date.today() + timedelta(days=-1))
            print("\tLoading data as live...")
            import_data(csv_text, entry_date, is_live)
            
            print("\tComplete")


def add_date_range(date_1, date_2):
    next_date = timedelta(days=1)
    current_date = date_1
    while current_date <= date_2:
        result = download_data_for_date(current_date)
        if result == '404':
            return
        current_date += next_date