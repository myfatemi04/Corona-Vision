import corona_sql
corona_sql.silent_mode = False

import upload

from data_sources.north_america import united_states as data

upload.upload_datapoints(data.import_data(), verbose=True)