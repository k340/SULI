#!/usr/bin/env python

"""Every 15 minutes, this script will check for new FT1 files from Fermi (mdcget)
    run search on farm for 12 hour intervals if new data in an interval is either > 1.2 * old
    or if it is the last interval of the day
    then send email to ltf-t for detections from ltf-b"""