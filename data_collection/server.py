from flask import Flask
from threading import Thread
import data_sources
import os

app = Flask(__name__)
@app.route("/")
def hello():
	return "Data import server"

def loop():
	while True:
		data_sources.import_live()

if __name__ == "__main__":
	Thread(name="Live data downloader", target=loop).start()
	PORT = 6060
	if "PORT" in os.environ:
		PORT = os.environ['PORT']
	app.run("0.0.0.0", port=PORT)