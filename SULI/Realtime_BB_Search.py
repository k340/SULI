#!/usr/bin/env python

"""Every 15 minutes, this script will check for new FT1 files from Fermi (mdcget)
    run search on farm for 12 hour intervals if new data in an interval is either > 1.2 * old
    or if it is the last interval of the day
    then send email to ltf-t for detections from ltf-b"""

import argparse
from GtBurst import mdcget

if __name__ == "__main__":

    parser = argparse.ArgumentParser('test')

    # add the arguments needed to the parser
    parser.add_argument('--date', help='Date of data to be searched')
    parser.add_argument('--test', dest='test_run', action='store_true')
    parser.set_defaults(test_run=False)

    # parse the arguments
    args = parser.parse_args()
