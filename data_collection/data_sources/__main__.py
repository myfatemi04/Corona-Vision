import corona_sql
corona_sql.silent_mode = False

import upload

from data_sources.north_america import mexico as data

upload.upload_datapoints(data.import_data(), verbose=True, force_update=True)