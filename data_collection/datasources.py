from import_gis import upload_geojson, upload_gis
from import_jhu import import_jhu_date, import_jhu_historical
from upload import upload
from datetime import datetime, date
from data_parser import import_table, import_json
import sys

def upload_usa_counties():
	upload_geojson(
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

def upload_italy_counties():
	upload_gis(
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

def upload_portugal_counties():
	upload_gis(
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

def upload_south_korea_provinces():
	upload_gis(
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

def upload_japan_provinces():
	try:
		upload(
			import_json(
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
		)
	except Exception as e:
		sys.stderr.write("Error during Japan provinces download: {} {}".format(type(e), e))

def upload_jhu_today():
	print("Uploading today's JHU data")
	upload(import_jhu_date(datetime.utcnow().date()))

def upload_jhu_historical():
	for data in import_jhu_historical():
		upload(data)

worldometers_disallow_countries = [
	'United States',
	'Italy',
	'Portugal',
	'South Korea',
	'Japan'
]
def upload_worldometers():
	print("Uploading live Worldometers data")
	try:
		upload(import_table(
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
		)
	except Exception as e:
		sys.stderr.write("Error during Worldometers download {} {}!".format(e, type(e)))

	# def delif(result, key):
	# 	if key in result:
	# 		del result[key]
	
	# for result in results['datapoint']:
	# 	if result in worldometers_disallow_countries:
	# 		delif(result, 'total')
	# 		delif(result, 'deaths')

	# upload(results)

def upload_live_usa_testing():
	print("Uploading Live USA testing")
	try:
		results = import_json(
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
		
		upload(results)
	except Exception as e:
		sys.stderr.write("Error during USA Testing download!".format(e, type(e)))

def upload_netherlands_counties():
	try:
		upload_gis(
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
	except Exception as e:
		sys.stderr.write("Error during Netherlands upload!".format(e, type(e)))

def upload_china_provinces_yesterday():
	print("Uploading China provinces")
	from datetime import datetime, timedelta
	yesterday = (datetime.utcnow().date() + timedelta(days=-1))
	url = yesterday.strftime("http://49.4.25.117/JKZX/yq_%Y%m%d.json")
	try:
		result = import_json(
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
		upload(result)
	except Exception as e:
		sys.stderr.write("Error loading China provinces: {} {}".format(type(e), e))

def upload_historical_usa_testing():
	print("Uploading historical USA testing")
	try:
		result = import_json(
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
		upload(result)
	except Exception as e:
		sys.stderr.write("Error during historical USA testing: {} {}".format(e, type(e)))
	
def upload_india_states():
	upload_gis(
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

def upload_all_live():
	upload_worldometers()
	upload_italy_counties()
	upload_portugal_counties()
	upload_south_korea_provinces()
	upload_japan_provinces()
	upload_usa_counties()
	upload_netherlands_counties()
	upload_india_states()
	upload_live_usa_testing()

def loop():
	while True:
		upload_all_live()

if __name__ == "__main__":
	upload_india_states()