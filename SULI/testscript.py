#!/usr/bin/env python

"this is a test script"

import argparse

if __name__=="__main__":

    parser = argparse.ArgumentParser('test')

    # add the arguments needed to the parser
    parser.add_argument("--test", help="some string", required=True, type=str)

    # parse the arguments
    args = parser.parse_args()

    print args.test