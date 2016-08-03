#!/usr/bin/env python

"""Takes text file containing grb names and outputs text file containing dates"""

import re
import argparse


def grb_name_to_date(grb_name):

    yy, mm, dd = re.match('([0-9]{2})([0-9]{2})([0-9]{2})', grb_name).groups()

    return '20%s-%s-%sT00:00:00' % (yy, mm, dd)

if __name__ == "__main__":

    parser = argparse.ArgumentParser('Get dates of GRBs')

    # add the arguments needed to the parser

    parser.add_argument("--in_file", help="Name of input file containing grb names", type=str, required=True)
    parser.add_argument("--out_file", help="Name of output file containing dates", type=str, required=True)

    # parse the arguments
    args = parser.parse_args()

    grbs = [line.rstrip('\n') for line in open(args.in_file)]

    with open(args.out_file + '.txt', 'w+') as f:

        for i in range(len(grbs) - 1):

            f.write("%s\n" % grb_name_to_date(grbs[i]))

        f.write("%s" % grb_name_to_date(grbs[len(grbs) - 1]))