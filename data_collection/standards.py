import pandas as pd
import numpy as np
import json

admin1_locations = {}
admin1_codes = {}
admin1_names = {}

country_locations = {}
country_codes = {}
country_names = {}
country_continents = {}

country_location_df = pd.read_csv("location_data/country_locations.tsv", sep='\t', keep_default_na=False, na_values=['_'])
for index, row in country_location_df.iterrows():
	country_code, lat, lng, country_name = row
	country_locations[country_code] = (lat, lng)
	country_codes[country_name.lower()] = country_code
	country_codes[country_name.split(",")[0].lower()] = country_code
	country_names[country_code] = country_name

us_admin1_location_df = pd.read_csv("location_data/us_state_locations.tsv", sep='\t')
for index, row in us_admin1_location_df.iterrows():
	admin1_code, lat, lng, admin1_name = row
	if not pd.isna(lat):
		admin1_locations['US'+"_"+admin1_code] = (lat, lng)
	admin1_codes['US'+"_"+admin1_name.lower()] = admin1_code
	admin1_names['US'+"_"+admin1_code] = admin1_name

# us_county_location_df = pd.read_csv("location_data/county_locations.txt", sep="|")
# county_locations = {}
# county_code_to_name = {}
# county_name_to_code = {}
# for index, row in us_county_location_df.iterrows():
# 	COUNTRY_CODE = "US"
# 	_, FEATURE_NAME, _, COUNTY_CODE, _, _, _, _, STATE_CODE, _, _, COUNTY_NAME, LAT, LONG, _, _ = row
# 	COUNTY_CODE = str(COUNTY_CODE)
# 	LAT = float(LAT)
# 	LONG = float(LONG)
# 	county_code_to_name[COUNTRY_CODE+"_"+STATE_CODE+"_"+COUNTY_CODE] = COUNTY_NAME
# 	county_name_to_code[COUNTRY_CODE+"_"+STATE_CODE+"_"+FEATURE_NAME] = COUNTY_CODE
# 	county_locations[COUNTRY_CODE+"_"+STATE_CODE+"_"+COUNTY_CODE] = LAT, LONG
	
# 	county_code_to_name[COUNTRY_CODE+"_"+STATE_CODE+"_"+COUNTY_CODE] = COUNTY_NAME
# 	county_name_to_code[COUNTRY_CODE+"_"+STATE_CODE+"_"+FEATURE_NAME] = COUNTY_CODE
# 	county_locations[COUNTRY_CODE+"_"+STATE_CODE+"_"+COUNTY_CODE] = LAT, LONG
# json.dump({"county_locations": county_locations, "county_code_to_name": county_code_to_name, "county_name_to_code": county_name_to_code}, open("location_data/counties.json", 'w'))
county_data = json.load(open("location_data/counties.json"))
county_locations = county_data['county_locations']
county_code_to_name = county_data['county_code_to_name']
county_name_to_code = county_data['county_name_to_code']

def get_county_location(country_name, admin1_name, county_name):
	if country_name is None:
		country_name = ''
	if admin1_name is None:
		admin1_name = ''
	if county_name is None:
		county_name = ''
	a0_code = get_country_code(country_name)
	a1_code = get_admin1_code(country_name, admin1_name)
	a2_code = get_county_code(country_name, admin1_name, county_name)
	if a0_code is not None and a1_code is not None and a2_code is not None:
		if (a0_code+"_"+a1_code+"_"+a2_code) in county_locations:
			return county_locations[a0_code+"_"+a1_code+"_"+a2_code]

def get_county_code(country_name, admin1_name, county_name):
	a0_code = get_country_code(country_name)
	a1_code = get_admin1_code(country_name, admin1_name)
	if a0_code is not None and a1_code is not None:
		if (a0_code+"_"+a1_code+"_"+county_name) in county_name_to_code:
			return county_name_to_code[a0_code+"_"+a1_code+"_"+county_name]

def get_country_location(country_name):
	country_code = get_country_code(country_name)
	if country_code in country_locations:
		return country_locations[country_code]

def get_country_code(country_name):
	if country_name.lower() in country_codes:
		return country_codes[country_name.lower()]
	elif country_name in country_codes.values():
		return country_name

def get_country_name(country_code):
	if country_code in country_names:
		return country_names[country_code]
	else:
		return country_code

def get_admin1_location(country_name, admin1_name):
	country_code = get_country_code(country_name)
	admin1_code = get_admin1_code(country_name, admin1_name)
	if admin1_code is not None and country_code is not None:
		if (country_code+"_"+admin1_code) in admin1_locations:
			return admin1_locations[country_code+"_"+admin1_code]

def get_admin1_code(country_name, admin1_name):
	country_code = get_country_code(country_name)
	admin1_name = admin1_name.split(", ")[-1]
	if country_code is not None:
		if (country_code+"_"+admin1_name.lower()) in admin1_codes:
			return admin1_codes[country_code+"_"+admin1_name.lower()]
		elif admin1_name in admin1_codes.values():
			return admin1_name

def get_admin1_name(country_name, admin1_code):
	country_code = get_country_code(country_name)
	if country_code is not None:
		if (country_code+"_"+admin1_code) in admin1_names:
			return admin1_names[country_code+"_"+admin1_code]
	return admin1_code

def get_estimated_location(country_name, admin1_name='', county=''):
	if county:
		return get_county_location(country_name, admin1_name, county)
	elif admin1_name:
		return get_admin1_location(country_name, admin1_name)
	elif country_name:
		return get_country_location(country_name)

fixes = {
	"uk": "United Kingdom",
	"us": "United States",
	"usa": "United States",
	"uae": "United Arab Emirates",
	"drc": "Congo, Democratic Republic of the",
	"car": "Central African Republic",
	"viet nam": "Vietnam"
}

in_fixes = {
	("china",): "China",
	("russia",): "Russia",
	("korea", "n."): "North Korea",
	("korea", "s."): "South Korea",
	("korea", "south"): "South Korea",
	("korea", "north"): "North Korea"
}

def remove_start(string, start):
	if string.lower().startswith(start):
		return string[len(start):]
	return string

def remove_end(string, end):
	if string.lower().endswith(end.lower()):
		return string[:-len(end)]
	return string

china_provinces = {
	"北京市": "Beijing",
	"天津市": "Tianjin",
	"河北省": "Hebei",
	"山西省": "Shanxi",
	"内蒙古自治区": "Inner Mongolia",
	"辽宁省": "Liaoning",
	"吉林省": "Jilin",
	"黑龙江省": "Heilongjiang",
	"上海市": "Shanghai",
	"江苏省": "Jiangsu",
	"浙江省": "Zhejiang",
	"安徽省": "Anhui",
	"福建省": "Fujian",
	"江西省": "Jiangxi",
	"山东省": "Shandong",
	"河南省": "Henan",
	"湖北省": "Hubei",
	"湖南省": "Hunan",
	"广东省": "Guangdong",
	"广西壮族自治区": "Guangxi Zhuang",
	"海南省": "Hainan",
	"重庆市": "Chongqing",
	"四川省": "Sichuan",
	"贵州省": "Guizhou",
	"云南省": "Yunnan",
	"西藏自治区": "Tibet",
	"陕西省": "Shaanxi",
	"甘肃省": "Gansu",
	"青海省": "Qinghai",
	"宁夏回族自治区": "Ningxia Hui",
	"新疆维吾尔自治区": "Xinjiang Uygur",
	"台湾省": "Taiwan",
	"香港特别行政区": "Hong Kong",
	"澳门特别行政区": "Macau"
}

import string
def normalize_name(country, admin1='', county=''):
	if country is None:
		country = ''
	if admin1 is None:
		admin1 = ''
	if county is None:
		county = ''

	country = str(country)
	admin1 = str(admin1)
	county = str(county)

	country = get_country_name(country)
	country = country.strip()
	admin1 = admin1.strip()
	county = county.strip()

	for req, fix in in_fixes.items():
		should_fix = True
		for part in req:
			if part not in country.lower():
				should_fix = False
		if should_fix:
			country = fix
			break
	
	for fix in fixes:
		if country.lower() == fix:
			country = fixes[fix]
			break

	country = remove_start(country, "the ")
	country = remove_start(country, "republic of")
	country = remove_end(country, ", the")
	country = remove_end(country, " (islamic republic of)")
	
	if country.lower() in ['overall', 'total', 'world']:
		country = ''

	if country == 'U.S.': country = "United States"
	if country.lower() == 'united states of america':
		country = 'United States'
	
	admin1 = admin1.replace("U.S.", "US")
	county = county.replace("U.S.", "US")

	if admin1.lower() == 'us military':
		admin1 = "US Military"

	if "grand princess" in admin1.lower():
		admin1 = "Grand Princess"

	# country = string.capwords(country)
	# admin1 = string.capwords(admin1)
	# county = string.capwords(county)

	if country == 'Hong Kong SAR':
		country = 'Hong Kong'
	if country == 'Guam':
		country = "United States"
		admin1 = "Guam"
	if country == 'Korea':
		country = 'South Korea'
	if country == "Faeroe Islands":
		country = "Faroe Islands"

	# swap admin1, county
	if admin1 == 'U.S.' and country=='United States':
		admin1 = county
		county = ''
	if 'SAR' in country:
		country = country.replace('SAR', '').strip()
	if admin1 == country:
		admin1 = county
		county = ''
	if admin1 == get_country_code(country):
		admin1 = county
		county = ''

	if 'Virgin Islands' in admin1 and country == 'United States':
		admin1 = 'Virgin Islands'
		country = 'United States'
	
	# # fix capitalization
	if admin1 != admin1.upper():
		admin1 = ' '.join([word.lower() if word.lower() in ['and', 'of'] else word for word in admin1.split()])

	if county != county.upper():
		county = ' '.join([word.lower() if word.lower() in ['and', 'of'] else word for word in county.split()])

	if ", " in admin1 and county == '':
		county, admin1 = get_county_admin1(country, admin1)

	admin1 = get_admin1_name(country, admin1) or admin1
	if country == 'United States' and admin1.lower() == "district of columbia":
		county = ''

	county = remove_end(county, " census area")
	county = remove_end(county, " and borough")
	county = remove_end(county, " borough")
	county = remove_end(county, " county")
	county = remove_end(county, " municipality")

	if admin1 in china_provinces:
		admin1 = china_provinces[admin1]

	if "diamond princess" in admin1.lower():
		admin1 = "Diamond Princess"
	if "wuhan" in admin1.lower() and "repatriated" in admin1.lower():
		admin1 = "Wuhan (repatriated)"
	if admin1.lower() == 'u.s. virgin islands':
		admin1 = 'Virgin Islands'
	return country, admin1, county

def cn_province_eng(admin1):
	if admin1 in china_provinces:
		return china_provinces[admin1]
	else:
		raise ValueError("Warning- Province not found- ", admin1)

def get_county_admin1(country, admin1):
	comma_index = admin1.rfind(", ")
	county, admin1_code = admin1[:comma_index], admin1[comma_index + 2:]
	if admin1_code:
		admin1_code = admin1_code.split()[0]
		admin1 = get_admin1_name(country, admin1_code) or admin1_code

		if admin1 == 'D.C.':
			admin1 = "District of Columbia"

	return county, admin1

continent_df = pd.read_csv('location_data/country_continent.csv')
alpha2_to_continent = {}
continent_codes = {
	"EU": "Europe",
	"AS": "Asia",
	"AF": "Africa",
	"OC": "Oceania",
	"NA": "North America",
	"SA": "South America",
	"AN": "Antarctica"
}
for _, row in continent_df.iterrows():
	iso, continent = row
	if pd.isna(continent): continent = 'NA'
	alpha2_to_continent[iso] = continent

def get_continent(country):
	country_code = get_country_code(country)
	if country_code in alpha2_to_continent:
		continent_code = alpha2_to_continent[country_code]
		return continent_codes[continent_code]
	else:
		return ''

if __name__ == "__main__":
	print("California location: ", get_admin1_location("US", "California"))
	print("AF code to name: ", get_country_name("AF"))
	print("Afghanistan name to code: ", get_country_code("Afghanistan"))
	print("SD code to location: ", get_country_location("SD"))
	print("Estimated location of Quebec, Canada: ", get_estimated_location("Canada", "Quebec"))
	print("Estimated location of France: ", get_estimated_location("France", ""))
	print("Estimated location of Virginia, US: ", get_estimated_location("United States", "Virginia"))
	print("State code of Virginia, US: ", get_admin1_code("United States", "Virginia"))
	print("Admin2/admin1 of Chicago, IL: ", get_county_admin1("US", "Chicago, IL"))
	print("GU state name: ", get_admin1_name("US", "GU"))
	# print("Location of Fairfax, Virginia, US: ", get_estimated_location("United States", "Alabama", "Colbert"))