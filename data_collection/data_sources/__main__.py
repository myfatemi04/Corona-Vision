import corona_sql
corona_sql.silent_mode = False

from . import india
india.import_data()

# import import_jhu
# import upload
# for result in import_jhu.import_jhu_historical():
#     upload.upload(result)