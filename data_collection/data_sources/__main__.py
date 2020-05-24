import corona_sql
corona_sql.silent_mode = False

import upload

import data_sources.europe.italy as data

upload.upload_datapoints(data.import_counties(), verbose=True)

import data_sources.worldometers

upload.upload_datapoints(data_sources.worldometers.import_data())