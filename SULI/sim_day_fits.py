#!/usr/bin/env python

"""This script takes a TSTART and ft2 file as input, and outputs a pair of fits files that contain
    24 hours of data. The ft1 files are simulated from the given tstart, and the ft2 are cut from input ft2.
    Output files are named as [output start time]_ft[1 or 2].fits
    Breaking the data into these smaller chunks is optimal for detection of short duration
    transients using a bayesian blocks algorithm"""

import argparse
import os
from astropy.io import fits
from SULI.execute_command import execute_command

# execute only if run from command line
if __name__ == "__main__":

    # create parser for this script
    parser = argparse.ArgumentParser(
        'Split Fermi data file (.fits) into multiple smaller files each spanning 24 hours by default')

    # add the arguments needed to the parser
    parser.add_argument("--tstart", help="TSTART for ft1 simulation", required=True, type=float)
    parser.add_argument("--in_ft2", help="Ft2 file containing data to be segmented", required=True, type=str)
    parser.add_argument("--buffer", help="Ft2 file is expanded backwards and forwards in time by this amount to ensure"
                                         "it covers a time interval >= Ft1", required=True, type=float)
    parser.add_argument("--n_days", help="Number of days to be simulated (default: 1)", type=int, default=1)
    parser.add_argument("--evclass", help="Event class to use for cutting the data (default: 128)", type=int,
                        default=128)
    parser.add_argument("--zmax", help="Zenith cut for the events", type=float, default=180)
    parser.add_argument("--interval", help="Length of time interval covered by output files (default 24 hours)",
                        type=float, default=86400.0)

    # parse the arguments
    args = parser.parse_args()

    # simulate ft1s from passed tstart, n_days
    for i in range(args.n_days):

        this_ft1_start = args.tstart + i * args.interval

        this_ft1_stop = args.tstart + (i + 1) * args.interval

        print "Intends to make ft1 beginning at %s, ending at %s (%sth file)" % (this_ft1_start, this_ft1_stop, i)

        cmd_line = "gtobssim infile=/home/suli_students/suli_kelin/simulation_input/3FGLSkyPass8R2/xml_files.txt " \
                   "srclist=/home/suli_students/suli_kelin/simulation_input/3FGLSkyPass8R2/source_names.txt " \
                   "scfile=%s " \
                   "evroot=%s " \
                   "simtime=%s " \
                   "tstart=%s " \
                   "use_ac=no " \
                   "emin=100 " \
                   "emax=100000 " \
                   "edisp=no " \
                   "irfs=P8R2_SOURCE_V6 " \
                   "evtype=none maxrows=1000000 " \
                   "seed=%s " \
                   "chatter=5" % (args.in_ft2, int(args.tstart), args.interval, args.tstart, int(args.tstart))

        # execute simulation
        execute_command(cmd_line)

        # rename output file
        last_ft1 = str(int(args.tstart)) + '_events_0000.fits'

        out_ft1 = str(int(args.tstart)) + '_ft1.fits'

        os.rename(os.path.join(os.getcwd(), last_ft1), os.path.join(os.getcwd(), out_ft1))

        # Update this_ft1_start and this_ft1_stop to ensure correct tstart, tstop
        # Probably obsolete
        with fits.open(out_ft1) as latest_ft1:

            this_ft1_start = max(latest_ft1[0].header['TSTART'],
                                 latest_ft1['GTI'].data.START.min())

            this_ft1_stop = min(latest_ft1[0].header['TSTOP'],
                                latest_ft1['GTI'].data.STOP.max())

        this_ft2_start = this_ft1_start - args.buffer

        this_ft2_stop = this_ft1_stop + args.buffer

        print "\nFt1 begins at %s, ends at %s (%sth cut)" % (this_ft1_start, this_ft1_stop, i)

        # Update the PROC_VER keyword if we are dealing with simulated data
        with fits.open(out_ft1, mode='update') as fits_file:

            if int(fits_file[0].header.get("PROC_VER")) < 100:

                # Simulated data

                print("Deadling with simulated data. Updating the PROC_VER keyword to '302'... ")

                fits_file[0].header.set("PROC_VER", "302")

        # cut ft2

        # prepare cut command
        out_ft2 = str(this_ft2_start) + '_ft2.fit'

        cmd_line = "ftcopy '%s[SC_DATA][START >= %s && STOP =< %s]' %s copyall=true" \
                   " clobber=true" % (args.in_ft2, this_ft2_start, this_ft2_stop, out_ft2)

        # execute cut
        execute_command(cmd_line)

        # Verify that the command executed and update the header

        with fits.open(out_ft2) as fits_file:

            # Check the start and stop in the binary table
            starts = fits_file['SC_DATA'].data.field("START")
            stops = fits_file['SC_DATA'].data.field("STOP")

            print '\nFt2 begins at %s, ends at %s \n' % (starts.min(), stops.max())

            if starts.min() - this_ft1_start > 0:

                raise RuntimeError("FT2 file starts after the FT1 file")

            if stops.max() - this_ft1_stop < 0:

                raise RuntimeError("FT2 file stops before the end of the FT1 file")

        print "Removing temporary file"

        # Update the header
        with fits.open(out_ft2, mode='update') as out_ft2:

            out_ft2['SC_DATA'].header.set("TSTART", starts.min())
            out_ft2['SC_DATA'].header.set("TSTOP", stops.max())

            out_ft2[0].header.set("TSTART", starts.min())
            out_ft2[0].header.set("TSTOP", stops.max())

    print "Finished"
