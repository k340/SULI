#!/usr/bin/env python

"""This script takes Fermi data in the form of a fits file as input, and outputs a set of fits files that each contain
    24 hours worth of input data. Output files are named as [input filename]_[output start time]_[output stop time].fits
    Breaking the data into these smaller chunks is optimal for detection of short duration
    transients using a bayesian blocks algorithm"""

import argparse
from GtApp import GtApp
from astropy.io import fits

# execute only if run from command line
if __name__=="__main__":

    # create parser for this script
    parser = argparse.ArgumentParser('Split Fermi data file (.fits) into multiple smaller files each spanning 24 hours')

    # add the arguments needed to the parser
    parser.add_argument("--in_file", help="Fits file containing data to be segmented", required=True,
                        type=str)

    # parse the arguments
    args = parser.parse_args()

    # get input data file from parser and retrieve start and stop times
    data = fits.open(args.in_file)

    begin = data[0].header['TSTART']
    end = data[0].header['TSTOP']

    # iterate over input file, creating new fits file for every 86400 seconds of data (24 hours)

    while begin < end:
        cut_time = begin + 86400

        gtselect = GtApp('gtselect')

        gtselect['infile'] = args.in_file

        gtselect['outfile'] = args.in_file.rsplit(".", 1)[0] + '_' + str(begin) + '_' + str(cut_time) + '.fits'

        gtselect['tmin'] = begin

        gtselect['tmax'] = cut_time

        gtselect.run()

        begin += 86400

    data.close()

