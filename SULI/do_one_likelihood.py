#!/usr/bin/env python

"""This script takes data from text files with 3 columns,
    obtains rad, deg, t1, t2
    uses these to perform likelihood analysis"""

import argparse

#empty script, takes rad, deg, t1, t2 as parameters

#execute only if run from command line
if __name__=="__main__":

    this_command = argparse.ArgumentParser('do_one_likelihood')

    this_command.add_argument("--ra",help="R.A. coordinate of input data", required=True)
    this_command.add_argument("--dec", help="Dec coordinate of input data", required=True)
    this_command.add_argument("--time_start", help="beginning of time interval for likelihood analysis",required=True)
    this_command.add_argument("--time_stop", help="end of time interval",required=True)

    args = this_command.parse_args()

    print(args.ra)
    print(args.dec)
    print(args.time_start)
    print(args.time_stop)

