#!/usr/bin/env python

"""This script takes Fermi data in the form of a fits file as input, and outputs a set of fits files that each contain
    24 hours worth of input data. Output files are named as [input filename]_[output start time]_[output stop time].fits
    Breaking the data into these smaller chunks is optimal for detection of short duration
    transients using a bayesian blocks algorithm"""

import argparse
from GtApp import GtApp
from astropy.io import fits
import numpy as np
from SULI.execute_command import execute_command

# execute only if run from command line
if __name__ == "__main__":

    # create parser for this script
    parser = argparse.ArgumentParser('Split Fermi data file (.fits) into multiple smaller files each spanning 24 hours')

    # add the arguments needed to the parser
    parser.add_argument("--in_ft1", help="Ft1 file containing data to be segmented", required=True,
                        type=str)
    parser.add_argument("--in_ft2", help="Ft2 file containing data to be segmented", required=True,
                        type=str)
    parser.add_argument("--buffer", help="Ft2 file is expanded backwards and forwards in time by this amount to ensure"
                                         "it covers a time interval >= Ft1", required=True)
    parser.add_argument("--evclass", help="Event class to use for cutting the data (default: 128)", required=True,
                        type=int)
    parser.add_argument("--zmax", help="Zenith cut for the events", required=True,
                        type=float)

    # parse the arguments
    args = parser.parse_args()

    # get input ft1 file from parser and retrieve start and stop times

    with fits.open(args.in_ft1) as ft1:

        event_file_start = ft1[0].header['TSTART']
        event_file_end = ft1[0].header['TSTOP']

    duration = event_file_end - event_file_start

    n_days = duration / 86400.0

    # print("Found %s days in file" % n_days)

    n_days_rounded = int(np.ceil(n_days))

    # print("Rounded up to %s" % n_days_rounded)

    # iterate over input ft1, creating new fits file for every 86400 seconds of data (24 hours)

    for i in range(n_days_rounded):

        this_start = event_file_start + i * 86400.0

        this_stop = event_file_start + (i+1) * 86400.0

        gtselect = GtApp('gtselect')

        gtselect['infile'] = args.in_ft1

        gtselect['outfile'] = args.in_ft1.rsplit(".", 1)[0] + '_' + str(this_start) + 'ft1.fits'

        gtselect['tmin'] = this_start

        gtselect['tmax'] = this_stop

        gtselect['evclass'] = args.evclass

        gtselect['zmax'] = args.zmax

        # Avoid cutting using an ROI

        gtselect['rad'] = 180.0

        # Avoid cutting in energy
        gtselect['emin'] = 10.0  # MeV
        gtselect['emax'] = 500000.0  # MeV

        gtselect.run()

    # pull relevant data interval from ft2 input

    with fits.open(args.in_ft2) as ft2:

        # add time buffers to cut

        event_file_start -= args.buffer
        event_file_end += args.buffer

        cmd_line = "ftcopy '%s[SC_DATA][START > %s && STOP < %s]' output_ft2.fit copyall=true'" % (ft2,
                                                                                                   event_file_start,
                                                                                                   event_file_end)
    execute_command(cmd_line)


'''First make this take an ft1 and ft2, gtsel on ft1 and do the other ftcopy thing on ft2 master to get ft2.
    then test whole thing on comp with data already have.
    then test on farm with random day. remember to log on:
        ssh -X suli_students@galprop-cluster
        go to your dir and cat instructions
        follow them
    this is the ftcopy thing:
    ftcopy '/nfs/data1/fermi_dm_simulation/FT2_tothefuture_1095722779.36.fits[SC_DATA][START > 243215772.532 && STOP < 243226804.137]' output_ft2.fit copyall=true
    might need to subprocess b/c command line'''


