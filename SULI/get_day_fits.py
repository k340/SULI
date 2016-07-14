#!/usr/bin/env python

"""This script takes Fermi data in the form of a fits file as input, and outputs a set of fits files that each contain
    24 hours worth of input data. Output files are named as [input filename]_[output start time]_[output stop time].fits
    Breaking the data into these smaller chunks is optimal for detection of short duration
    transients using a bayesian blocks algorithm"""

import argparse
import os
import numpy as np
from GtApp import GtApp
from astropy.io import fits
from SULI.execute_command import execute_command

# execute only if run from command line
if __name__ == "__main__":

    # create parser for this script
    parser = argparse.ArgumentParser(
        'Split Fermi data file (.fits) into multiple smaller files each spanning 24 hours by default')

    # add the arguments needed to the parser
    parser.add_argument("--in_ft1", help="Ft1 file containing data to be segmented", required=True,
                        type=str)
    parser.add_argument("--in_ft2", help="Ft2 file containing data to be segmented", required=True,
                        type=str)
    parser.add_argument("--buffer", help="Ft2 file is expanded backwards and forwards in time by this amount to ensure"
                                         "it covers a time interval >= Ft1", required=True, type=float)
    parser.add_argument("--evclass", help="Event class to use for cutting the data (default: 128)", required=True,
                        type=int)
    parser.add_argument("--zmax", help="Zenith cut for the events", required=True,
                        type=float)
    parser.add_argument("--interval", help="Length of time interval covered by output files (default 24 hours)",
                        type=float, default=86400.0)

    # parse the arguments
    args = parser.parse_args()

    # get input ft1 file from parser and retrieve start and stop times

    with fits.open(args.in_ft1) as ft1:

        event_file_start = ft1[0].header['TSTART']
        event_file_end = ft1[0].header['TSTOP']

    duration = event_file_end - event_file_start

    n_days = duration / args.interval

    print("Found %s intervals in file" % n_days)

    n_days_rounded = int(np.ceil(n_days))

    print("Rounded up to %s \n" % n_days_rounded)

    # iterate over input files creating new fits file for every 86400 seconds of data (24 hours)

    for i in range(n_days_rounded):

        this_ft1_start = event_file_start + i * args.interval

        this_ft1_stop = event_file_start + (i + 1) * args.interval

        temp_ft1 = "__temp%s_ft1.fit" % i

        print "Intends to make ft1 cut beginning at %s, ending at %s (%sth cut)" % (this_ft1_start, this_ft1_stop, i)

        # Pre-cut the FT1 file for speed
        cmd_line = "ftcopy '%s[EVENTS][TIME > %s && TIME < %s]' %s copyall=true " \
                   "clobber=true" % (args.in_ft1, this_ft1_start - 1000.0, this_ft1_stop + 1000.0, temp_ft1)

        # execute cut
        execute_command(cmd_line)

        # cut ft1
        out_ft1 = str(this_ft1_start) + '_ft1.fit'

        gtselect = GtApp('gtselect')

        gtselect['infile'] = temp_ft1

        gtselect['outfile'] = out_ft1

        gtselect['tmin'] = this_ft1_start

        gtselect['tmax'] = this_ft1_stop

        gtselect['evclass'] = args.evclass

        gtselect['zmax'] = args.zmax

        # Avoid cutting using an ROI
        gtselect['rad'] = 180.0

        # Avoid cutting in energy
        gtselect['emin'] = 10.0  # MeV
        gtselect['emax'] = 500000.0  # MeV

        gtselect.run()

        # Update this_ft1_start and this_ft1_stop to reflect what was actually considered by gtselect, which
        # only considers good time intervals

        with fits.open(out_ft1) as latest_ft1:

            this_ft1_start = latest_ft1[0].header['TSTART']

            this_ft1_stop = latest_ft1[0].header['TSTOP']

        this_ft2_start = this_ft1_start - args.buffer

        this_ft2_stop = this_ft1_stop + args.buffer

        print "\nFt1 cut begins at %s, ends at %s (%sth cut)" % (this_ft1_start, this_ft1_stop, i)

        # cut ft2

        # prepare cut command
        out_name = str(this_ft2_start) + '_ft2.fit'

        cmd_line = "ftcopy '%s[SC_DATA][START > %s && STOP < %s]' %s copyall=true" \
                   " clobber=true" % (args.in_ft2, this_ft2_start, this_ft2_stop, out_name)

        # execute cut
        execute_command(cmd_line)

        # Verify that the command executed and update the header

        with fits.open(out_name) as out_ft2:

            # Check the start and stop in the binary table
            starts = out_ft2['SC_DATA'].data.field("START")
            stops = out_ft2['SC_DATA'].data.field("STOP")

            print '\nFt2 begins at %s, ends at %s \n' % (starts.min(), stops.max())

            if starts.min() - this_ft1_start > 0:

                raise RuntimeError("FT2 file starts after the FT1 file")

            if stops.max() - this_ft1_stop < 0:

                raise RuntimeError("FT2 file stops before the end of the FT1 file")

        print "Removing temporary file"
        os.remove(temp_ft1)

        # Update the header
        with fits.open(out_name, mode='update') as out_ft2:

            out_ft2['SC_DATA'].header.set("TSTART", starts.min())
            out_ft2['SC_DATA'].header.set("TSTOP", stops.max())

            out_ft2[0].header.set("TSTART", starts.min())
            out_ft2[0].header.set("TSTOP", stops.max())

            '''header order is date-end, tstart, tstop, timesys'''
'''test whole thing on comp with data already have.
    then test on farm with random day. remember, to log on:
        ssh -X suli_students@galprop-cluster
        go to your dir and cat instructions
        follow them
    this is the ftcopy thing:
    ftcopy '/nfs/data1/fermi_dm_simulation/FT2_tothefuture_1095722779.36.fits[SC_DATA][START > 243215772.532 && STOP < 243226804.137]' output_ft2.fit copyall=true'''