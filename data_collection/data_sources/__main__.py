import corona_sql
corona_sql.silent_mode = False

from . import bermuda
for row in bermuda.import_data():
    print(row)

# import import_jhu
# import upload
# for result in import_jhu.import_jhu_historical():
#     upload.upload(result)