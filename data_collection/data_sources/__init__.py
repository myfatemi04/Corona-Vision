
minWait = 60 * 360

import traceback
import sys

from . import albania
from . import australia
from . import azerbaijan
from . import bahrain
from . import canada
from . import china
from . import france
from . import india
from . import italy
from . import japan
from . import netherlands
from . import portugal
from . import south_korea
from . import spain
from . import united_states

from . import worldometers

from . import usa_testing

live = [
	albania.import_data,
	australia.import_data,
	azerbaijan.import_data,
	bahrain.import_data,
	canada.import_data,
	france.import_data,
	india.import_data,
	italy.import_data,
	japan.import_data,
	netherlands.import_data,
	portugal.import_data,
	south_korea.import_data,
	spain.import_data,
	united_states.import_data,
	worldometers.import_data,

	usa_testing.import_data
]

def import_group(l):
	for fn in l:
		try:
			fn()
		except Exception as e:
			sys.stderr.write("Exception during group data import: {} [type {}]".format(e, type(e)))
			traceback.print_tb(e.__traceback__)

def import_live():
	import_group(live)

def import_jhu_historical():
	from import_jhu import import_jhu_date, import_jhu_historical
	import upload
	for data in import_jhu_historical():
		upload.upload(data)
