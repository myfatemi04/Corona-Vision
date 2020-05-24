from flask import Flask
from threading import Thread
import data_sources
import os

app = Flask(__name__)
@app.route("/")
def hello():
	return "Data import server."

def loop():
	import corona_sql
	corona_sql.silent_mode = True
	while True:
		data_sources.import_group('live')

if __name__ == "__main__":
	current = "[booting...]"

	# Start the downloader
	Thread(name="Data downloader", target=loop, daemon=True).start()

	# Get the PORT from environment variables
	PORT = 6060 if "PORT" not in os.environ else os.environ['PORT']

	app.run("0.0.0.0", port=PORT, threaded=True)
