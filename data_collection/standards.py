import pandas as pd
import numpy as np
import json

province_locations = {}
province_codes = {}
province_names = {}

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

us_province_location_df = pd.read_csv("location_data/us_state_locations.tsv", sep='\t')
for index, row in us_province_location_df.iterrows():
	province_code, lat, lng, province_name = row
	if not pd.isna(lat):
		province_locations['US'+"_"+province_code] = (lat, lng)
	province_codes['US'+"_"+province_name.lower()] = province_code
	province_names['US'+"_"+province_code] = province_name

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

def get_county_location(country_name, province_name, county_name):
	if country_name is None:
		country_name = ''
	if province_name is None:
		province_name = ''
	if county_name is None:
		county_name = ''
	a0_code = get_country_code(country_name)
	a1_code = get_province_code(country_name, province_name)
	a2_code = get_county_code(country_name, province_name, county_name)
	if a0_code is not None and a1_code is not None and a2_code is not None:
		if (a0_code+"_"+a1_code+"_"+a2_code) in county_locations:
			return county_locations[a0_code+"_"+a1_code+"_"+a2_code]

def get_county_code(country_name, province_name, county_name):
	a0_code = get_country_code(country_name)
	a1_code = get_province_code(country_name, province_name)
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

def get_province_location(country_name, province_name):
	country_code = get_country_code(country_name)
	province_code = get_province_code(country_name, province_name)
	if province_code is not None and country_code is not None:
		if (country_code+"_"+province_code) in province_locations:
			return province_locations[country_code+"_"+province_code]

def get_province_code(country_name, province_name):
	country_code = get_country_code(country_name)
	province_name = province_name.split(", ")[-1]
	if country_code is not None:
		if (country_code+"_"+province_name.lower()) in province_codes:
			return province_codes[country_code+"_"+province_name.lower()]
		elif province_name in province_codes.values():
			return province_name

def get_province_name(country_name, province_code):
	country_code = get_country_code(country_name)
	if country_code is not None:
		if (country_code+"_"+province_code) in province_names:
			return province_names[country_code+"_"+province_code]
	return province_code

def get_estimated_location(country_name, province_name='', county=''):
	if county:
		return get_county_location(country_name, province_name, county)
	elif province_name:
		return get_province_location(country_name, province_name)
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
def normalize_name(country, province='', county=''):
	if country is None:
		country = ''
	if province is None:
		province = ''
	if county is None:
		county = ''

	country = str(country)
	province = str(province)
	county = str(county)

	country = get_country_name(country)
	country = country.strip()
	province = province.strip()
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
	
	province = province.replace("U.S.", "US")
	county = county.replace("U.S.", "US")

	if province.lower() == 'us military':
		province = "US Military"

	if "grand princess" in province.lower():
		province = "Grand Princess"

	# country = string.capwords(country)
	# province = string.capwords(province)
	# county = string.capwords(county)

	if country == 'Hong Kong SAR':
		country = 'Hong Kong'
	if country == 'Guam':
		country = "United States"
		province = "Guam"
	if country == 'Korea':
		country = 'South Korea'
	if country == "Faeroe Islands":
		country = "Faroe Islands"

	# swap province, county
	if province == 'U.S.' and country=='United States':
		province = county
		county = ''
	if 'SAR' in country:
		country = country.replace('SAR', '').strip()
	if province == country:
		province = county
		county = ''
	if province == get_country_code(country):
		province = county
		county = ''

	if 'Virgin Islands' in province and country == 'United States':
		province = 'Virgin Islands'
		country = 'United States'
	
	# # fix capitalization
	if province != province.upper():
		province = ' '.join([word.lower() if word.lower() in ['and', 'of'] else word for word in province.split()])

	if county != county.upper():
		county = ' '.join([word.lower() if word.lower() in ['and', 'of'] else word for word in county.split()])

	if ", " in province and county == '':
		county, province = get_county_province(country, province)

	province = get_province_name(country, province) or province
	if country == 'United States' and province.lower() == "district of columbia":
		county = ''

	county = remove_end(county, " census area")
	county = remove_end(county, " and borough")
	county = remove_end(county, " borough")
	county = remove_end(county, " county")
	county = remove_end(county, " municipality")

	if province in china_provinces:
		province = china_provinces[province]

	if "diamond princess" in province.lower():
		province = "Diamond Princess"
	if "wuhan" in province.lower() and "repatriated" in province.lower():
		province = "Wuhan (repatriated)"
	if province.lower() == 'u.s. virgin islands':
		province = 'Virgin Islands'
	return country, province, county

def cn_province_eng(province):
	if province in china_provinces:
		return china_provinces[province]
	else:
		raise ValueError("Warning- Province not found- ", province)

def get_county_province(country, province):
	comma_index = province.rfind(", ")
	county, province_code = province[:comma_index], province[comma_index + 2:]
	if province_code:
		province_code = province_code.split()[0]
		province = get_province_name(country, province_code) or province_code

		if province == 'D.C.':
			province = "District of Columbia"

	return county, province

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
	print("California location: ", get_province_location("US", "California"))
	print("AF code to name: ", get_country_name("AF"))
	print("Afghanistan name to code: ", get_country_code("Afghanistan"))
	print("SD code to location: ", get_country_location("SD"))
	print("Estimated location of Quebec, Canada: ", get_estimated_location("Canada", "Quebec"))
	print("Estimated location of France: ", get_estimated_location("France", ""))
	print("Estimated location of Virginia, US: ", get_estimated_location("United States", "Virginia"))
	print("State code of Virginia, US: ", get_province_code("United States", "Virginia"))
	print("Admin2/province of Chicago, IL: ", get_county_province("US", "Chicago, IL"))
	print("GU state name: ", get_province_name("US", "GU"))
	# print("Location of Fairfax, Virginia, US: ", get_estimated_location("United States", "Alabama", "Colbert"))