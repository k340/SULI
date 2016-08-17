#!/usr/bin/env python

"""Every 15 minutes, this script will check for new FT1 files from Fermi (mdcget)
    run search on farm for 12 hour intervals if new data in an interval is either > 1.2 * old
    or if it is the last interval of the day
    then send email to ltf-t for detections from ltf-b"""

import argparse
from subprocess import check_call
from ltfException import ltfException
import datetime
import time
import dateutil

if __name__ == "__main__":

    parser = argparse.ArgumentParser('RTS')

    # add the arguments needed to the parser
    parser.add_argument('--date', help='Date of data to be searched')
    parser.add_argument('--test', dest='test_run', action='store_true')
    parser.set_defaults(test_run=False)

    # parse the arguments
    args = parser.parse_args()

    from GtBurst.dataHandling import date2met

    # Check that the date is a valid date
    try:

        validated = dateutil.parser.parse(args.date).isoformat().replace("T", " ")
    except:

        raise ltfException("Invalid ISO date")

    # check each of the defined intervals
    def check_int(met_start):

        check_call("mdcget --met_start %s --met_stop %s") % (met_start, met_start + 43200)

    # interval 1 begins at 00:00:00
    met_start_1 = date2met(validated)
    check_call("mdcget --met_start %s --met_stop %s") % (met_start_1, met_start_1 + 43200)
    pass

    ''''# interval 2 begins at 06:00:00
    met_start_2 = met_start_1 + 21600
    check_call("mdcget --met_start %s --met_stop %s") % (met_start_2, met_start_2 + 43200)
    pass

    # interval 3 begins at 12:00:00
    met_start_3 = met_start_1 + 43200
    check_call("mdcget --met_start %s --met_stop %s") % (met_start_3, met_start_3 + 43200'''
