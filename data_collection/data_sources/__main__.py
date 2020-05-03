import corona_sql
corona_sql.silent_mode = False

from . import us_states
us_states.massachusetts.import_data()