#!/usr/bin/env python

"""This is a global script that takes actual or simulated Fermi data and searches it for transients
    actual data is specified by a date, simulated is given by a specific ft1 or ft2 file"""

import argparse
import subprocess as sub
from astropy.io import fits

# execute only if run from command line
if __name__ == "__main__":

    # create parser for this script
    parser = argparse.ArgumentParser('Search input data for Transients')

    # add the arguments needed to the parser

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--date', help='date specifying file to download')
    group.add_argument('--inp_fts', help='filenames of ft1 and ft2 input, separated by a comma (ex: foo.ft1,bar.ft2)')

    parser.add_argument("--evclass", help="Event class to use for cutting the data (default: 128)", type=int,
                        required=True)
    parser.add_argument("--probability", help="Probability of null hypothesis", type=float, required=True)
    parser.add_argument("--min_dist", help="Distance above which regions are not considered to overlap", type=float,
                        required=True)
    parser.add_argument("--out_file", help="Name of text file containing list of possible transients", type=str,
                        required=True)
    parser.add_argument("--loglevel", help="Level of log detail (DEBUG, INFO)")
    parser.add_argument("--logfile", help="Name of logfile")
    parser.add_argument("--workdir", help="Path of work directory")
    # parser.add_argument("--zmax", help="Maximum zenith allowed for data to be considered", required=True, type=float)

    # parse the arguments
    args = parser.parse_args()

    # if using real data
    if args.date:

        # bayesian blocks
        sub.check_call('ltfsearch.py --date ' + str(args.date) + ' --duration 86400.0 --irfs ' + str(args.evclass) +
                       ' --probability ' + str(args.probability) + ' --loglevel ' + str(args.loglevel) + ' --logfile ' +
                       str(args.logfile) + ' --workdir ' + str(args.workdir) + ' --outfile active_file.txt',
                       shell=True)

        # remove redundant triggers
        sub.check_call('remove_redundant_regions.py --in_list active_file.txt --min_dist ' + str(args.min_dist) +
                       ' --out_list ' + str(args.out_file), shell=True)

    # else using simulated data
    else:

        # get names of ft1 and ft2 files
        ft1_name = args.inp_fts.rsplit(",", 1)[0]
        ft2_name = args.inp_fts.rsplit(",", 1)[1]

        sim_start = 0
        sim_end = 1

        with fits.open(str(ft1_name)) as ft1:

            sim_start = ft1[0].header['TSTART']
            sim_end = ft1[0].header['TSTOP']

        dur = sim_end - sim_start

        # bayesian blocks
        sub.check_call('ltfsearch.py --date ' + str(sim_start) + ' --duration ' + str(dur) + ' --irfs ' +
                       str(args.evclass) + ' --probability ' + str(args.probability) + ' --loglevel ' +
                       str(args.loglevel) + ' --logfile ' + str(args.logfile) + ' --workdir ' + str(args.workdir) +
                       ' --outfile active_file.txt --ft1 ' + str(ft1_name) + ' --ft2 ' + str(ft2_name), shell=True)

        # remove redundant triggers
        sub.check_call('remove_redundant_regions.py --in_list active_file.txt --min_dist ' + str(args.min_dist) +
                       ' --out_list ' + str(args.out_file), shell=True)
