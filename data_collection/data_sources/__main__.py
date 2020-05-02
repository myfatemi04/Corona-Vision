import corona_sql
corona_sql.silent_mode = False

from . import france
france.import_historical_data()