#!/usr/bin/env python

"""This script takes data from text files with 3 columns,
    obtains rad, deg, t1, t2
    uses these to perform likelihood analysis"""

import argparse

#empty script, takes rad, deg, t1, t2 as parameters

#execute only if run from command line
if __name__=="__main__":

    this_command = argparse.ArgumentParser("likelihood_script")

    this_command.add_argument("--rad",help="rad coordinate of input data", required=True)
    this_command.add_argument("--deg", help="deg coordinate of input data", required=True)
    this_command.add_argument("--time_start", help="beginning of time interval for likelihood analysis",required=True)
    this_command.add_argument("--time_stop", help="end of time interval",required=True)

    args = this_command.parse_args()

    print(args.rad)
    print(args.deg)
    print(args.time_start)
    print(args.time_stop)

