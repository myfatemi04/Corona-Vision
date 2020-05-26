"""
Usage: data.py [-g <group>] [-d <source-name>] [--verbose] [--force-update] [--repeat]

-g <group>              The group to upload from.
-d <source-name>        The data source to download.
--verbose               Prints out data as it goes.
--force-update          Updates totals, even if there were no changes.
--repeat                Will repeat the data uploads forever.
"""

import corona_sql
corona_sql.silent_mode = False

import data_sources
import upload
import docopt

args = docopt.docopt(__doc__)
verbose = args['--verbose']
force_update = args['--force-update']

repeat = args['--repeat']
done_once = False

if args['-d'] is not None:
    data_source_name = args['-d']
    while repeat or not done_once:
        data_sources.import_by_name(data_source_name, verbose=verbose, force_update=force_update)
        done_once = True
elif args['-g'] is not None:
    while repeat or not done_once:
        data_sources.import_group(args['-g'], verbose=verbose, force_update=force_update)
        done_once = True
else:
    print(__doc__)

# upload.upload_datapoints(data.import_counties(), verbose=True)

