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
    parser.add_argument("--directory", help="Location of files to be searched", type=str,
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

    files = [f for f in listdir(args.directory) if (str(join(args.directory, f)).endswith(('.fits', '.fit')))]
    files.sort()

    for i in range(len(files) / 2):

        # ft2 always start before ft1, so come first alphabetically

        nft2 = 2 * i
        nft1 = 2 * i + 1

        with fits.open(files[nft2]) as ft2:
            file_start = ft2[0].header['TSTART']

        out_name = str(file_start) + '.txt'

        cmd_line = 'search_for_transients.py --inp_fts %s,%s --irf %s --probability %s --min_dist %s ' \
                   '--out_file %s' % (args.directory + files[nft1], args.directory + files[nft2], args.irf,
                                      args.min_dist, args.probability, out_name)

        execute_command(cmd_line)
