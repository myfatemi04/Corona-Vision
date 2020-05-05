from . import massachusetts
from . import newjersey
from . import virginia
import traceback

def import_data():
    import server
    for state in [
        massachusetts,
        newjersey,
        virginia,
    ]:
        try:
            print("Importing data from", state.__name__, "...")
            server.current = state.__name__
            state.import_data()
        except Exception as e:
            traceback.print_tb(e.__traceback__)