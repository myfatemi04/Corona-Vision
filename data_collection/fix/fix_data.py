from datetime import datetime, date, timedelta
from corona_sql import Datapoint, Session
import time

"""

A toolset of functions to fix data where u done messed up

"""
def update_all_deltas():
    import recounting
    start_date = date(2020, 1, 22)
    end_date = datetime.utcnow().date()
    while start_date <= end_date:
        recounting.update_deltas(start_date, None)
        next_day = start_date + timedelta(days=1)
        start_date = next_day

def recalculate_selection(*where):
    import recounting
    session = Session()
    results = session.query(Datapoint).filter(*where)
    updates = set()
    for result in results:
        updates.update(result.ripples())
    recounting.recount(updates, session)
    session.commit()

def delete_dp(*where):
    import recounting
    print("Here is your input: ", *where)
    print("Is this OK?")
    input("Make sure there's an entry date, and you aren't missing any fields.")
    input("You're 100% sure?")
    print("Deleting")
    
    session = Session()
    results = session.query(Datapoint).filter(*where)
    updates = set()
    for result in results:
        updates.add(result.ripples())
        session.delete(result)

    recounting.recount(updates, session)
    print("Committing in 10 seconds")
    time.sleep(10)
    session.commit()
    print("Complete")

if __name__ == "__main__":
    pass