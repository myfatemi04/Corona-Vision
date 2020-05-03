import requests
import time
import upload
import standards
from data_parser import import_table

lastDatapointsUpdate = 0
minWait = 60

disallowed = [
	"Albania",
	"Argentina",
	"Australia",
	"Azerbaijan",
	"Bahrain",
	"Canada",
	"France",
	"Germany",
	"India",
	"Italy",
	"Japan",
	"Netherlands",
	"Portugal",
	"South Korea",
	"Spain",
	"United States",
]

def import_data():
	global lastDatapointsUpdate

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

	# def delif(result, key):
	# 	if key in result:
	# 		del result[key]
	
	# newDatapoints = []
	# for result in results['datapoint']:
	# 	result['country'], _, _ = standards.normalize_name(result['country'], '', '')
	# 	if result['country'] not in disallowed:
	# 		newDatapoints.append(result)

	if upload.upload_datapoints(results['datapoint'], "http://www.worldometers.info/coronavirus"):			
		lastDatapointsUpdate = time.time()

def getSources():
	from bs4 import BeautifulSoup
	import datetime

	textContent = requests.get("http://www.worldometers.info/coronavirus").text
	soup = BeautifulSoup(textContent, "html.parser")

	# select whichever news date is "today"
	firstNews = soup.select_one(time.strftime("#newsdate%Y-%m-%d"))
	
	# find list elements
	elements = firstNews.select("li")

	for elem in elements:
		country = elem.select_one("strong > a")
		newsSource = elem.select_one(".news_source_a")
		if country and newsSource:
			print(country.text, newsSource['href'])
	