
minWait = 60 * 5

import traceback
import sys

from . import albania
from . import australia
from . import argentina
from . import azerbaijan
from . import bahrain
from . import brazil
from . import canada
from . import china
from . import czechia
from . import france
from . import germany
from . import india
from . import italy
from . import japan
from . import netherlands
from . import nigeria
from . import norway
from . import portugal
from . import russia
from . import south_korea
from . import spain
from . import turkey
from . import united_states

from . import worldometers

from . import usa_testing

live = [
	albania,
	argentina,
	# australia,
	azerbaijan,
	bahrain,
	brazil,
	canada,
	czechia,
	france,
	germany,
	india,
	italy,
	japan,
	netherlands,
	nigeria,
	norway,
	portugal,
	russia,
	south_korea,
	spain,
	united_states,
	turkey,
	worldometers,

	usa_testing
]

def import_group(l):
	for module in l:
		try:
			print("Importing data from", module.__name__, "...")
			module.import_data()
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
