from corona_sql import *

def fix_location_names():
    print("Fixing location names...")
    session = Session()
    all_countries = session.query(Datapoint)
    for row in all_countries:
        session = Session()
        country, province, admin2, entry_date = row.country, row.province, row.admin2, row.entry_date

        # normalize the name
        new_country, new_province, new_admin2 = standards.normalize_name(country, province, admin2)

        # see if the normalized name is different
        if new_country == country and new_province == province and new_admin2 == admin2:
            continue
        else:
            print(country, province, admin2, entry_date, "-->", new_country, new_province, new_admin2)

        # check if an entry with the fixed name already exists
        real_name = session.query(Datapoint).filter_by(country=new_country, province=new_province, admin2=new_admin2, entry_date=entry_date).first()
        old_name = row

        if real_name:
            print("Found a duplicate")
            # update the row that has the real name, and remove the row with the fake name
            for label in ['total', 'deaths', 'recovered', 'active', 'num_tests', 'serious']:
                if getattr(old_name, label) > getattr(real_name, label):
                    setattr(real_name, label, getattr(old_name, label))
            
            for l in ['dtotal', 'ddeaths', 'drecovered', 'dactive', 'dserious', 'latitude', 'longitude', 'source_total', 'source_deaths', 'source_recovered', 'source_num_tests', 'source_serious']:
                if not getattr(real_name, l) and getattr(old_name, l):
                    setattr(real_name, l, getattr(old_name, l))
            session.delete(old_name)
        else:
            print("Found no duplicates")
            # update the row with the fake name to have the correct name
            old_name.country = new_country
            old_name.province = new_province
            old_name.admin2 = new_admin2
            
    session.commit()

# this is like a CS lab
def remove_duplicates():
    print("Removing duplicates...")
    session = Session()
    seen = {}
    rows = session.query(Datapoint).all()
    for row in rows:
        primary = row.country.lower(), row.province.lower(), row.admin2.lower(), row.entry_date
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
# remove_duplicates()

# country_overall = calc_overall_country("China", "2020-04-16", session)
# print(country_overall)

# dates = [result[0] for result in sess.query(Datapoint.entry_date).distinct().order_by(Datapoint.entry_date).all()]

# print("This day   Day before")
# for x in range(1, len(dates) - 1):
# 	today, yesterday = dates[x], dates[x - 1]
# 	print(today, yesterday)
# today_datapoints = sess.query(Datapoint).filter_by(entry_date=today)
# yesterday_datapoints = sess.query(Datapoint).filter_by(entry_date=yesterday)
# today_dict = {(d.country, d.province, d.admin2): d for d in today_datapoints}
# yesterday_dict = {(d.country, d.province, d.admin2): d for d in yesterday_datapoints}

# total = len(today_dict)

# for location in today_dict:
#     if location in yesterday_dict:
#         daily_active = today_dict[location].active - yesterday_dict[location].active
#         today_dict[location].dactive = daily_active

# sess.commit()

# today_dp = sess.query(Datapoint).filter_by(entry_date='2020-04-15')
# live_dp = sess.query(Datapoint).filter_by(entry_date='live')
# today_mapped = {(dp.country, dp.province, dp.admin2): dp for dp in today_dp}

# # update live dactives
# for dp in live_dp:
# 	location = dp.country, dp.province, dp.admin2
# 	if location not in today_mapped:
# 		dp.dactive = 0
# 	else:
# 		dp.dactive = today_mapped[location].dactive

# # fix belgium
# entry_dates = "2020-02-04 2020-02-05 2020-02-06 2020-02-07 2020-02-08 2020-02-09 2020-02-10 2020-02-11 2020-02-12 2020-02-13 2020-02-14 2020-02-15 2020-02-16 2020-02-17 2020-02-18 2020-02-19 2020-02-20 2020-02-21 2020-02-22 2020-02-23 2020-02-24 2020-02-25 2020-02-26 2020-02-27 2020-02-28 2020-02-29 2020-03-01 2020-03-02 2020-03-03 2020-03-04 2020-03-05 2020-03-06 2020-03-07 2020-03-08 2020-03-09 2020-03-10 2020-03-11 2020-03-12 2020-03-13 2020-03-14 2020-03-15 2020-03-16 2020-03-17 2020-03-18 2020-03-19 2020-03-20 2020-03-21 2020-03-22 2020-03-23 2020-03-24 2020-03-25 2020-03-26 2020-03-27 2020-03-28 2020-03-29 2020-03-30 2020-03-31 2020-04-01 2020-04-02 2020-04-03 2020-04-04 2020-04-05 2020-04-06 2020-04-07 2020-04-08 2020-04-09 2020-04-10 2020-04-11 2020-04-12 2020-04-13 2020-04-14 2020-04-15 2020-04-16".split()
# total = "1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 2 8 54 65 50 122 169 200 239 267 314 350 559 689 886 1058 1243 1486 1795 2257 2815 3401 3743 4269 4937 6235 7284 9134 10836 11899 12775 13964 15348 16770 18431 19691 20814 22194 23403 24983 26667 28018 29647 30589 31119 33573 33573".split()]
# deaths = "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 3 3 3 4 4 5 10 14 21 37 67 75 88 122 178 220 289 353 431 513 705 828 1011 1143 1283 1447 1632 2035 2240 2523 3019 3346 3600 3903 4157 4440 4440".split()]
# recovered = "0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 31 31 1 263 263 401 461 547 675 858 1063 1359 1527 1696 2132 2495 2872 3247 3751 3986 4157 4681 5164 5568 5986 6463 6707 6868 7107 7107".split()]
# dtotal = [int(x) for x in "1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 6 0 0 27 0 0 0 0 0 0 0 0 0 197 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 2454".split()
# ddeaths = [int(x) for x in "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 283".split()
# drecovered = [int(x) for x in "0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0".split()

# print("Committing...")
# sess.commit()

# add continents
# import standards
# # countries = standards.country_names.values()
# sess = Session()
# countries = [c[0] for c in sess.query(Datapoint.country).distinct().all()]
# i = 0
# for country in countries:
#     i += 1
#     continent = standards.get_continent(country)
#     print(f'\r{i}/{len(countries)} {country}', end='                          \r')
#     sess.query(Datapoint).filter_by(country=country).update({'group': continent})
#     sess.commit()