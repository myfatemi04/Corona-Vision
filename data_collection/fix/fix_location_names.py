from corona_sql import *

def fix_location_names():
    print("Fixing location names...")
    session = Session()
    all_countries = session.query(Datapoint)
    for row in all_countries:
        session = Session()
        country, province, county, entry_date = row.country, row.province, row.county, row.entry_date

        # normalize the name
        new_country, new_province, new_county = standards.normalize_name(country, province, county)

        # see if the normalized name is different
        if new_country == country and new_province == province and new_county == county:
            continue
        else:
            print(country, province, county, entry_date, "-->", new_country, new_province, new_county)

        # check if an entry with the fixed name already exists
        real_name = session.query(Datapoint).filter_by(country=new_country, province=new_province, county=new_county, entry_date=entry_date).first()
        old_name = row

        if real_name:
            print("Found a duplicate")
            # update the row that has the real name, and remove the row with the fake name
            for label in ['total', 'deaths', 'recovered', 'tests', 'serious']:
                if getattr(old_name, label) > getattr(real_name, label):
                    setattr(real_name, label, getattr(old_name, label))
                    
            session.delete(old_name)
        else:
            print("Found no duplicates")
            # update the row with the fake name to have the correct name
            old_name.country = new_country
            old_name.province = new_province
            old_name.county = new_county
            
    session.commit()

# this is like a CS lab
def remove_duplicates():
    print("Removing duplicates...")
    session = Session()
    seen = {}
    rows = session.query(Datapoint).all()
    for row in rows:
        primary = row.country.lower(), row.province.lower(), row.county.lower(), row.entry_date
        if primary in seen:
            # if it's been seen before, merge them together
            other = seen[primary]
            
            # delete the one that wasn't original
            session.delete(row)

            for label in ['total', 'deaths', 'recovered', 'active', 'num_tests', 'serious']:
                if getattr(row, label) > getattr(other, label):
                    setattr(other, label, getattr(row, label))
            
            for l in ['dtotal', 'ddeaths', 'drecovered', 'dactive', 'dserious']:
                if not getattr(other, l) and getattr(row, l):
                    setattr(other, l, getattr(row, l))

            print("Updated", primary)
        else:
            seen[primary] = row

    print("Committing...")
    session.commit()

fix_location_names()