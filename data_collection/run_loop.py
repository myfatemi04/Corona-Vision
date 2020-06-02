"""
Runs a loop that collects data from the 'live' group of data_sources.
By default, it waits thirty minutes between intervals. This is so the
Google Cloud costs will be cheaper.

However, to keep our data live and accurate, we must also collect it
at the start of every day, sharp. This is so daily counts are aligned
along the same time.

Author: Michael Fatemi
June 6th, 2020
"""

import data_sources
import datetime, time

lastUpdate = None

# Shorthand, becaues we use UTC time
now = lambda: datetime.datetime.utcnow()

# Main loop, goes on forever
while True:
    # This will happen on the first iteration
    if lastUpdate is None:
        data_sources.import_group('live')
        lastUpdate = now()

    # Otherwise, we need to check how much time has passed
    else:
        difference = now() - lastUpdate

        # If 30 minutes have passed or it's a new day
        if difference.min >= 30 or now().date() > lastUpdate.date():
            data_sources.import_group('live')
            lastUpdate = now()

    time.sleep(60)