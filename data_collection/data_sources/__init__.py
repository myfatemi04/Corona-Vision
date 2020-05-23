
minWait = 60 * 5

from collections import defaultdict

data_groups = defaultdict(list)

def source(*group_names, name=''):
    def add_source(func):
        for group_name in group_names:
            data_groups[group_name].append((func, name))

        return func

    return add_source

import traceback
import sys
import upload

from . import albania, australia, argentina, azerbaijan
from . import bahrain, brazil, bermuda
from . import canada, china, czechia
from . import france
from . import gabon, germany
from . import india, italy
from . import japan
from . import netherlands, niger, nigeria, norway
from . import portugal
from . import russia
from . import south_korea, spain
from . import turkey
from . import united_states, uganda, us_states, usa_testing
from . import worldometers

def import_group(name):
    for func, func_name in data_groups[name]:
        try:
            print("Importing data from", func_name, "...")
            results = [datapoint for datapoint in func()]
            upload.upload_datapoints(results)
        except Exception as e:
            sys.stderr.write("Exception during group data import: {} [type {}]".format(e, type(e)))
            traceback.print_tb(e.__traceback__)

def import_live():
    import_group('live')

def import_jhu_historical():
    from import_jhu import import_jhu_date, import_jhu_historical
    import upload
    for data in import_jhu_historical():
        upload.upload(data)
