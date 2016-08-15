#!/usr/bin/env python

"""this is a test script that prints whatever argument is passed to it from the command line"""

import argparse
import subprocess as sub

if __name__ == "__main__":

    parser = argparse.ArgumentParser('test')

    # add the arguments needed to the parser
    parser.add_argument('--test', dest='test_run', action='store_true')
    parser.set_defaults(test_run=False)

    # parse the arguments
    args = parser.parse_args()

    x = sub.check_output("qstat", shell=True)

    print x
