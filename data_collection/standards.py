import pandas as pd
import numpy as np
import json

admin1_locations = {}
admin1_codes = {}
admin1_names = {}

admin0_locations = {}
admin0_codes = {}
admin0_names = {}
admin0_continents = {}

admin0_location_df = pd.read_csv("location_data/country_locations.tsv", sep='\t', keep_default_na=False, na_values=['_'])
for index, row in admin0_location_df.iterrows():
	admin0_code, lat, lng, admin0_name = row
	admin0_locations[admin0_code] = (lat, lng)
	admin0_codes[admin0_name.lower()] = admin0_code
	admin0_codes[admin0_name.split(",")[0].lower()] = admin0_code
	admin0_names[admin0_code] = admin0_name

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
admin2_data = json.load(open("location_data/counties.json"))
admin2_locations = admin2_data['county_locations']
admin2_code_to_name = admin2_data['county_code_to_name']
admin2_name_to_code = admin2_data['county_name_to_code']

def get_admin2_location(admin0_name, admin1_name, admin2_name):
	if admin0_name is None:
		admin0_name = ''
	if admin1_name is None:
		admin1_name = ''
	if admin2_name is None:
		admin2_name = ''
	a0_code = get_admin0_code(admin0_name)
	a1_code = get_admin1_code(admin0_name, admin1_name)
	a2_code = get_admin2_code(admin0_name, admin1_name, admin2_name)
	if a0_code is not None and a1_code is not None and a2_code is not None:
		if (a0_code+"_"+a1_code+"_"+a2_code) in admin2_locations:
			return admin2_locations[a0_code+"_"+a1_code+"_"+a2_code]

def get_admin2_code(admin0_name, admin1_name, admin2_name):
	a0_code = get_admin0_code(admin0_name)
	a1_code = get_admin1_code(admin0_name, admin1_name)
	if a0_code is not None and a1_code is not None:
		if (a0_code+"_"+a1_code+"_"+admin2_name) in admin2_name_to_code:
			return admin2_name_to_code[a0_code+"_"+a1_code+"_"+admin2_name]

def get_admin0_location(admin0_name):
	admin0_code = get_admin0_code(admin0_name)
	if admin0_code in admin0_locations:
		return admin0_locations[admin0_code]

def get_admin0_code(admin0_name):
	if admin0_name.lower() in admin0_codes:
		return admin0_codes[admin0_name.lower()]
	elif admin0_name in admin0_codes.values():
		return admin0_name

def get_admin0_name(admin0_code):
	if admin0_code in admin0_names:
		return admin0_names[admin0_code]
	else:
		return admin0_code

def get_admin1_location(admin0_name, admin1_name):
	admin0_code = get_admin0_code(admin0_name)
	admin1_code = get_admin1_code(admin0_name, admin1_name)
	if admin1_code is not None and admin0_code is not None:
		if (admin0_code+"_"+admin1_code) in admin1_locations:
			return admin1_locations[admin0_code+"_"+admin1_code]

def get_admin1_code(admin0_name, admin1_name):
	admin0_code = get_admin0_code(admin0_name)
	admin1_name = admin1_name.split(", ")[-1]
	if admin0_code is not None:
		if (admin0_code+"_"+admin1_name.lower()) in admin1_codes:
			return admin1_codes[admin0_code+"_"+admin1_name.lower()]
		elif admin1_name in admin1_codes.values():
			return admin1_name

def get_admin1_name(admin0_name, admin1_code):
	admin0_code = get_admin0_code(admin0_name)
	if admin0_code is not None:
		if (admin0_code+"_"+admin1_code) in admin1_names:
			return admin1_names[admin0_code+"_"+admin1_code]
	return admin1_code

def get_estimated_location(admin0_name, admin1_name='', admin2=''):
	if admin2:
		return get_admin2_location(admin0_name, admin1_name, admin2)
	elif admin1_name:
		return get_admin1_location(admin0_name, admin1_name)
	elif admin0_name:
		return get_admin0_location(admin0_name)

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
def normalize_name(admin0, admin1='', admin2=''):
	if admin0 is None:
		admin0 = ''
	if admin1 is None:
		admin1 = ''
	if admin2 is None:
		admin2 = ''

	admin0 = str(admin0)
	admin1 = str(admin1)
	admin2 = str(admin2)

	admin0 = get_admin0_name(admin0)
	admin0 = admin0.strip()
	admin1 = admin1.strip()
	admin2 = admin2.strip()

	for req, fix in in_fixes.items():
		should_fix = True
		for part in req:
			if part not in admin0.lower():
				should_fix = False
		if should_fix:
			admin0 = fix
			break
	
	for fix in fixes:
		if admin0.lower() == fix:
			admin0 = fixes[fix]
			break

	admin0 = remove_start(admin0, "the ")
	admin0 = remove_start(admin0, "republic of")
	admin0 = remove_end(admin0, ", the")
	admin0 = remove_end(admin0, " (islamic republic of)")
	
	if admin0.lower() in ['overall', 'total', 'world']:
		admin0 = ''

	if admin0 == 'U.S.': admin0 = "United States"
	if admin0.lower() == 'united states of america':
		admin0 = 'United States'
	
	admin1 = admin1.replace("U.S.", "US")
	admin2 = admin2.replace("U.S.", "US")

	if admin1.lower() == 'us military':
		admin1 = "US Military"

	if "grand princess" in admin1.lower():
		admin1 = "Grand Princess"

	# admin0 = string.capwords(admin0)
	# admin1 = string.capwords(admin1)
	# admin2 = string.capwords(admin2)

	if admin0 == 'Hong Kong SAR':
		admin0 = 'Hong Kong'
	if admin0 == 'Guam':
		admin0 = "United States"
		admin1 = "Guam"
	if admin0 == 'Korea':
		admin0 = 'South Korea'
	if admin0 == "Faeroe Islands":
		admin0 = "Faroe Islands"

	# swap admin1, admin2
	if admin1 == 'U.S.' and admin0=='United States':
		admin1 = admin2
		admin2 = ''
	if 'SAR' in admin0:
		admin0 = admin0.replace('SAR', '').strip()
	if admin1 == admin0:
		admin1 = admin2
		admin2 = ''
	if admin1 == get_admin0_code(admin0):
		admin1 = admin2
		admin2 = ''

	if 'Virgin Islands' in admin1 and admin0 == 'United States':
		admin1 = 'Virgin Islands'
		admin0 = 'United States'
	
	# # fix capitalization
	if admin1 != admin1.upper():
		admin1 = ' '.join([word.lower() if word.lower() in ['and', 'of'] else word for word in admin1.split()])

	if admin2 != admin2.upper():
		admin2 = ' '.join([word.lower() if word.lower() in ['and', 'of'] else word for word in admin2.split()])

	if ", " in admin1 and admin2 == '':
		admin2, admin1 = get_admin2_admin1(admin0, admin1)

	admin1 = get_admin1_name(admin0, admin1) or admin1
	if admin0 == 'United States' and admin1.lower() == "district of columbia":
		admin2 = ''

	admin2 = remove_end(admin2, " census area")
	admin2 = remove_end(admin2, " and borough")
	admin2 = remove_end(admin2, " borough")
	admin2 = remove_end(admin2, " county")
	admin2 = remove_end(admin2, " municipality")

	if admin1 in china_provinces:
		admin1 = china_provinces[admin1]

	if "diamond princess" in admin1.lower():
		admin1 = "Diamond Princess"
	if "wuhan" in admin1.lower() and "repatriated" in admin1.lower():
		admin1 = "Wuhan (repatriated)"
	if admin1.lower() == 'u.s. virgin islands':
		admin1 = 'Virgin Islands'
	return admin0, admin1, admin2

def cn_province_eng(admin1):
	if admin1 in china_provinces:
		return china_provinces[admin1]
	else:
		raise ValueError("Warning- Province not found- ", admin1)

def get_admin2_admin1(admin0, admin1):
	comma_index = admin1.rfind(", ")
	admin2, admin1_code = admin1[:comma_index], admin1[comma_index + 2:]
	if admin1_code:
		admin1_code = admin1_code.split()[0]
		admin1 = get_admin1_name(admin0, admin1_code) or admin1_code

		if admin1 == 'D.C.':
			admin1 = "District of Columbia"

	return admin2, admin1

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

def get_continent(admin0):
	admin0_code = get_admin0_code(admin0)
	if admin0_code in alpha2_to_continent:
		continent_code = alpha2_to_continent[admin0_code]
		return continent_codes[continent_code]
	else:
		return ''

if __name__ == "__main__":
	print("California location: ", get_admin1_location("US", "California"))
	print("AF code to name: ", get_admin0_name("AF"))
	print("Afghanistan name to code: ", get_admin0_code("Afghanistan"))
	print("SD code to location: ", get_admin0_location("SD"))
	print("Estimated location of Quebec, Canada: ", get_estimated_location("Canada", "Quebec"))
	print("Estimated location of France: ", get_estimated_location("France", ""))
	print("Estimated location of Virginia, US: ", get_estimated_location("United States", "Virginia"))
	print("State code of Virginia, US: ", get_admin1_code("United States", "Virginia"))
	print("Admin2/admin1 of Chicago, IL: ", get_admin2_admin1("US", "Chicago, IL"))
	print("GU state name: ", get_admin1_name("US", "GU"))
	# print("Location of Fairfax, Virginia, US: ", get_estimated_location("United States", "Alabama", "Colbert"))