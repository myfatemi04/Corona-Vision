import corona_sql
corona_sql.silent_mode = False

import upload

import data_sources.asia.india

upload.upload_datapoints(data_sources.asia.india.import_data())