
minWait = 60 * 5

import traceback
import sys

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

live = [
    albania,
    argentina,
    # australia,
    azerbaijan,
    bahrain,
    bermuda,
    brazil,
    canada,
    czechia,
    france,
    gabon,
    germany,
    india,
    italy,
    japan,
    netherlands,
    niger,
    nigeria,
    norway,
    portugal,
    russia,
    south_korea,
    spain,
    turkey,
    united_states,
    uganda,
    worldometers,

    usa_testing,
    us_states
]

def import_group(l):
    import server
    for module in l:
        try:
            print("Importing data from", module.__name__, "...")
            server.current = module.__name__
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
