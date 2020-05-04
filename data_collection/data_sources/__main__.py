import corona_sql
corona_sql.silent_mode = False

from . import france
france.import_data()

# import import_jhu
# import upload
# for result in import_jhu.import_jhu_historical():
#     upload.upload(result)