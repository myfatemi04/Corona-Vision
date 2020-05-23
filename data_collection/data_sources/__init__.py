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

import data_sources.africa
import data_sources.australia
import data_sources.asia
import data_sources.europe
import data_sources.north_america
import data_sources.south_america

import data_sources.worldometers

def import_group(name, verbose=False):
    for func, func_name in data_groups[name]:
        try:
            print("Importing data from", func_name, "...")
            results = [datapoint for datapoint in func()]
            upload.upload_datapoints(results, verbose)
        except Exception as e:
            sys.stderr.write("Exception during group data import: {} [type {}]".format(e, type(e)))
            traceback.print_tb(e.__traceback__)

def import_jhu_historical():
    from import_jhu import import_jhu_date, import_jhu_historical
    import upload
    for data in import_jhu_historical():
        upload.upload(data)
