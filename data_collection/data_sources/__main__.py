import corona_sql
corona_sql.silent_mode = False

from . import united_states
united_states.import_hist_counties()
