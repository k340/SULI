#!/usr/bin/env python

"""This script runs search_for_transients.py on all fits file pairs in folder passed as argument
    This is obviously only appropriately used for simulated data"""

import argparse
from astropy.io import fits
import os
from os import listdir
from os.path import isfile, join

from SULI.execute_command import execute_command

# execute only if run from command line
if __name__ == "__main__":

    # create parser for this script
    parser = argparse.ArgumentParser('Search input folder')

    # add the arguments needed to the parser
    parser.add_argument("--ft1folder", help="Location of ft1 files to be searched", type=str,
                        required=True)
    parser.add_argument("--ft2folder", help="Location of ft2 files to be searched", type=str,
                        required=True)
    parser.add_argument("--irf", help="Instrument response function name to be used", type=str,
                        required=True)
    parser.add_argument("--probability", help="Probability of null hypothesis", type=float, required=True)
    parser.add_argument("--min_dist", help="Distance above which regions are not considered to overlap", type=float,
                        required=True)
    parser.add_argument("--loglevel", help="Level of log detail (DEBUG, INFO)", default='info')
    parser.add_argument("--logfile", help="Name of logfile for the ltfsearch.py script", default='ltfsearch.log')
    parser.add_argument("--workdir", help="Path of work directory", default=os.getcwd())

    # parse the arguments
    args = parser.parse_args()

    # get list of ft1 files
    ft1_files = [f for f in listdir(args.directory) if (str(join(args.directory, f)).endswith(('ft1.fits', 'ft1.fit')))]
    ft1_files.sort()

    # get list of ft2 files
    ft2_files = [f for f in listdir(args.directory) if (str(join(args.directory, f)).endswith(('ft2.fits', 'ft2.fit')))]
    ft2_files.sort()

    # make sure each ft1/ft2 is part of a pair
    if len(ft1_files) != len(ft2_files):

        if len(ft1_files) > len(ft2_files):

            x = 'ft1 files'
            y = 'ft2 files'

        else:

            x = 'ft2 files'
            y = 'ft1 files'

        raise RuntimeError('There are more %s than %s' % (x, y))

    # for each ft1 in folder, run search_for_transients.py using it and its partner ft2 as arguments
    # assumes all ft files are paired and ordered
    for i in range(len(ft1_files)):

        # use start time of ft1 for outfile name, since ft2 starts early due to buffer
        with fits.open(args.directory + '/' + ft1_files[i]) as ft1:

            file_start = ft1[0].header['TSTART']

        out_name = str(file_start) + '.txt'

        cmd_line = 'search_for_transients.py --inp_fts %s,%s --irf %s --probability %s --min_dist %s --out_file %s' % (
                                                                args.directory + '/' + ft1_files[i],
                                                                args.directory + '/' + ft2_files[i], args.irf, args.min_dist,
                                                                args.probability, out_name)

        execute_command(cmd_line)
