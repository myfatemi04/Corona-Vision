from import_gis import import_geojson, import_gis
from import_jhu import import_jhu_date, import_jhu_historical
from upload import upload, upload_datapoints
from datetime import datetime, date
from data_parser import import_table, import_json
import traceback
import requests
import standards
import time
import sys
import io

def import_usa_counties():
	return import_geojson(
		source_url="https://coronavirus-resources.esri.com/datasets/628578697fb24d8ea4c32fa0c5ae1843_0?geometry=112.752%2C22.406%2C19.764%2C64.233&showData=true",
		query_url="https://opendata.arcgis.com/datasets/628578697fb24d8ea4c32fa0c5ae1843_0.geojson",
		table_labels={
			"location": {
				"country": ["Country_Region"],
				"province": ["Province_State"],
				"county": ["Admin2"],
				"latitude": ["Lat"],
				"longitude": ["Long_"]
			},
			"datapoint": {
				"country": ["Country_Region"],
				"province": ["Province_State"],
				"county": ["Admin2"],
				"total": ["Confirmed"],
				"recovered": ["Recovered"],
				"deaths": ["Deaths"]
			}
		}
	)

def import_italy_counties():
	return import_gis(
		"https://services6.arcgis.com/L1SotImj1AAZY1eK/arcgis/rest/services/dpc_regioni_covid19/FeatureServer/0/",
		{
			"location" :{
				"country": "Italy",
				"province": ["denominazione_regione"],
				"latitude": ["latitudine"],
				"longitude": ["longitudine"],
			},
			"datapoint": {
				"country": "Italy",
				"province": ["denominazione_regione"],
				"total": ["totale_casi"],
				"deaths": ["deceduti"]
			}
		}
	)

def import_portugal_counties():
	return import_gis(
		"http://services.arcgis.com/CCZiGSEQbAxxFVh3/ArcGIS/rest/services/COVID19_Concelhos_V/FeatureServer/0/",
		{
			"location": {
				"country": "Portugal",
				"province": ["Distrito", "::cap"],
				"county": ["Concelho", "::cap"]
			},
			"datapoint": {
				"country": "Portugal",
				"province": ["Distrito", "::cap"],
				"county": ["Concelho", "::cap"],
				"deaths": ["Obitos_Conc"],
				"recovered": ["Recuperados_Conc"],
				"total": ["ConfirmadosAcumulado_Conc"]
			}
		}
	)

def import_south_korea_provinces():
	return import_gis(
		"https://services2.arcgis.com/RiHDI9SnFmD3Itzs/arcgis/rest/services/%EC%8B%9C%EB%8F%84%EB%B3%84_%EC%BD%94%EB%A1%9C%EB%82%98/FeatureServer/0/",
		{
			"location": {
				"country": "South Korea",
				"province": ["CTP_ENG_NM"]
			},
			"datapoint": {
				"country": "South Korea",
				"province": ["CTP_ENG_NM"],
				"total": ["발생자수"],
				"deaths": ["사망자수"],
			}
		}
	)

def import_japan_provinces():
	return import_json(
		url="https://data.covid19japan.com/summary/latest.json",
		source_link="https://covid19japan.com",
		table_labels={
			"datapoint": {
				"country": "Japan",
				"province": ["name"],
				"total": ["confirmed"],
				"deaths": ["deaths"],
				"recovered": ["recovered"]
			}
		},
		namespace=["prefectures"]
	)

def import_jhu_today():
	print("Importing today's JHU data")
	return import_jhu_date(datetime.utcnow().date())

def upload_jhu_historical():
	for data in import_jhu_historical():
		upload(data)

worldometers_disallow_countries = {
	"United States": ["tests"]
}
def import_worldometers():
	print("Uploading live Worldometers data")
	results = import_table(
		"http://www.worldometers.info/coronavirus",
		["#main_table_countries_today", 0],
		{
			"datapoint": {
				"country": ["Country,  Other"],
				"total": ["Total  Cases", "::number"],
				"deaths": ["Total  Deaths", "::number"],
				"serious": ["Serious,  Critical", "::number"],
				"tests": ["Total  Tests", "::number"],
				"recovered": ["Total  Recovered", "::number"]
			}
		}
	)

	def delif(result, key):
		if key in result:
			del result[key]
	
	for result in results['datapoint']:
		result['country'], _, _ = standards.normalize_name(result['country'], '', '')
		if result['country'] in worldometers_disallow_countries:
			for feature in worldometers_disallow_countries[result['country']]:
				delif(result, feature)

	return results

def import_live_usa_testing():
	print("Uploading Live USA testing")
	return import_json(
		url="https://covidtracking.com/api/v1/states/current.json",
		source_link="https://covidtracking.com",
		table_labels={
			"datapoint": {
				"country": "United States",
				"province": ["state", "::us_state_code"],
				"tests": ["totalTestResults"],
				"hospitalized": ["hospitalizedCurrently"],
				"recovered": ["recovered"]
			}
		},
		namespace=[]
	)

def import_netherlands_counties():
	return import_gis(
		"https://services.arcgis.com/nSZVuSZjHpEZZbRo/arcgis/rest/services/Coronavirus_RIVM_vlakken_actueel/FeatureServer/0//",
		table_labels={
			"datapoint": {
				"country": "Netherlands",
				"province": ["Provincie"],
				"county": ["Gemeentenaam"],
				"total": ["Meldingen"],
				"hospitalized": ["Ziekenhuisopnamen"],
				"deaths": ["Overleden"]
			},
			"location": {
				"country": "Netherlands",
				"province": ["Provincie"],
				"county": ["Gemeentenaam"],
				"population": ["Bevolkingsaantal", "::dividethousands"]
			}
		}
	)

def import_china_provinces_yesterday():
	print("Uploading China provinces")
	from datetime import datetime, timedelta
	yesterday = (datetime.utcnow().date() + timedelta(days=-1))
	url = yesterday.strftime("http://49.4.25.117/JKZX/yq_%Y%m%d.json")
	return import_json(
		url=url,
		source_link="https://ncov.dxy.cn/ncovh5/view/en_pneumonia",
		table_labels={
			"datapoint": {
				"country": "China",
				"province": ["properties", "省份", "::china_province_eng"],
				"total": ["properties", "累计确诊"],
				"deaths": ["properties", "累计死亡"],
				"entry_date": yesterday
			}
		},
		namespace=["features"]
	)

def import_historical_usa_testing():
	print("Uploading historical USA testing")
	results = import_json(
		url="https://covidtracking.com/api/v1/states/daily.json",
		source_link="https://covidtracking.com",
		table_labels={
			"datapoint": {
				"entry_date": ["date", "::str", "::ymd"],
				"country": "United States",
				"province": ["state", "::us_state_code"],
				"tests": ["total"],
				"hospitalized": ["hospitalized"],
				"recovered": ["recovered"]
			}
		},
		namespace=[]
	)
	results['datapoint'] = [result for result in results['datapoint'] if result['entry_date'] == date(2020, 4, 22)]
	return results
	
def import_india_states():
	return import_gis(
		gis_url="https://utility.arcgis.com/usrsvcs/servers/83b36886c90942ab9f67e7a212e515c8/rest/services/Corona/DailyCasesMoHUA/MapServer/0/",
		table_labels={
			"datapoint": {
				"country": "India",
				"province": ["state_name"],
				"total": ["confirmedcases"],
				"recovered": ["cured_discharged_migrated"],
				"deaths": ["deaths"]
			}
		},
		use_geometry=False
	)

live = [
	import_worldometers,
	import_italy_counties,
	import_portugal_counties,
	import_south_korea_provinces,
	import_japan_provinces,
	import_usa_counties,
	import_netherlands_counties,
	import_india_states,
	import_live_usa_testing
]

def upload_all_live():
	for f in live:
		try:
			upload(f())
		except Exception as e:
			sys.stderr.write("Error during an import!")
			traceback.print_tb(e.__traceback__)

def upload_social_distancing():
	import pandas as pd
	import json

	response = requests.get("https://www.gstatic.com/covid19/mobility/Global_Mobility_Report.csv")
	if response.status_code == 200:
		csv_data = response.text
		df = pd.read_csv(io.StringIO(csv_data), keep_default_na=False, na_values=[])
		content = []
		content2 = []
		i = 0
		for _, row in df.iterrows():
			i += 1
			print(f"\rLoading {i}/{len(df)}...", end='\r')
			new_datapoint = {
				'entry_date': datetime.strptime(row['date'], "%Y-%m-%d").date(),
				# 'country': (row['country_region']),
				# 'province': (row['sub_region_1']),
				# 'county': (row['sub_region_2']),
				'country': fix_name(row['country_region']),
				'province': fix_name(row['sub_region_1']),
				'county': fix_name(row['sub_region_2']),
				'retail_change': row['retail_and_recreation_percent_change_from_baseline'] or 0,
				'grocery_change': row['grocery_and_pharmacy_percent_change_from_baseline'] or 0,
				'parks_change': row['parks_percent_change_from_baseline'] or 0,
				'transit_change': row['transit_stations_percent_change_from_baseline'] or 0,
				'workplaces_change': row['workplaces_percent_change_from_baseline'] or 0,
				'residential_change': row['residential_percent_change_from_baseline'] or 0
			}
			content.append(new_datapoint)
			content2.append({**new_datapoint, "entry_date": new_datapoint['entry_date'].strftime("%Y-%m-%d")})
		upload_datapoints(content, source_link='', recount=False)
		json.dump(content2, open("social-distancing.json", "w"))
		
def fix_name(s):
	return s.encode("cp1252", errors='replace').decode("cp1252")

def socdist_loop():
	while True:
		upload_social_distancing()
		time.sleep(60 * 60 * 4)

def loop():
	while True:
		upload_all_live()

if __name__ == "__main__":
	pass # upload_social_distancing()