import traceback
import sys

from . import albania
from . import china
from . import india
from . import italy
from . import japan
from . import netherlands
from . import portugal
from . import south_korea
from . import united_states

from . import worldometers

from . import usa_testing

live = [
	albania.import_data,
	india.import_data,
	italy.import_data,
	japan.import_data,
	netherlands.import_data,
	portugal.import_data,
	south_korea.import_data,
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