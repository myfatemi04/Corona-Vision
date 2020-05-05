from flask import Flask
from threading import Thread
import data_sources
import os

app = Flask(__name__)
@app.route("/")
def hello():
	return "Data import server"

def loop():
	import corona_sql
	corona_sql.silent_mode = True
	while True:
		data_sources.import_live()

if __name__ == "__main__":
	loop()