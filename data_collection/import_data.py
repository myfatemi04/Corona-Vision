from flask import Flask
from threading import Thread
import downloader
import os

app = Flask(__name__)
@app.route("/")
def hello():
	return "Data import server"

if __name__ == "__main__":
	using_server = "coronavision_import_data_use_server" not in os.environ
	Thread(name="Live data downloader", target=downloader.loop, daemon=not using_server).start()
	# Thread(name="Social distancing data downloader", target=datasources.socdist_loop, daemon=not using_server).start()
	if using_server:
		PORT = 6060
		if "PORT" in os.environ:
			PORT = os.environ['PORT']
		app.run("0.0.0.0", port=PORT)
	else:
		input()