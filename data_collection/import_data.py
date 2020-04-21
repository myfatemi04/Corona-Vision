from datetime import date, timedelta, datetime
from bs4 import BeautifulSoup
from flask import Flask, redirect
from threading import Thread
from upload import upload
from json_extractor import find_json, extract_json_row, json_methods, number
import fix_data
from import_gis import import_gis
import chardet
import json

# data processing
import pandas as pd
import numpy as np

# native python
import traceback
import time
import json
import sys
import os
import io

import requests
import standards
import import_jhu

# def allowed(result, regex):
# 	import re
# 	for attr, pattern in regex.items():
# 		table, label = attr.split(".")
# 		if not re.match(pattern, result[table][label]):
# 			return False
# 	return True

# def upload_datasource(datasource):
# 	try:
# 		args = datasource['args']
# 		method = methods[datasource['method']]
# 		results = method(**args)
# 		if results:
# 			if "regex" in datasource:
# 				# for each result, go through all the filters and see if they match. if not any of them match, then they're ok.
# 				results = [result for result in results if allowed(result, datasource['regex'])]

# 			upload(results)
# 	except Exception as e:
# 		print("Error during update: ", e, type(e), ". Data source: ", datasource['label'])
# 		traceback.print_tb(sys.exc_info()[2])

app = Flask(__name__)

@app.route("/")
def hello():
	return redirect("https://www.coronavision.us/")

if __name__ == "__main__":
	use_server = "coronavision_import_data_use_server" not in os.environ

	if use_server:
		PORT = 6060
		if "PORT" in os.environ:
			PORT = os.environ['PORT']
		app.run("0.0.0.0", port=PORT)
	else:
		input()