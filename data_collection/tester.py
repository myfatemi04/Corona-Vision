import data_sources
import corona_sql
corona_sql.silent_mode = False

while True:
	data_sources.import_group('live')