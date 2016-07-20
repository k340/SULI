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
from SULI.numsuf import numsuf

# execute only if run from command line
if __name__ == "__main__":

    # create parser for this script
    parser = argparse.ArgumentParser(
        'Split Fermi data file (.fits) into multiple smaller files each spanning 24 hours by default')

    # add the arguments needed to the parser
    parser.add_argument("--tstart", help="TSTART for ft1 simulation", required=True, type=float)
    parser.add_argument("--in_ft2", help="Ft2 file containing data to be segmented", required=True, type=str)
    parser.add_argument("--src_dir", help="Directory containing the input files for the simulation "
                                          "(XML file, spectra, source names and so on...)", required=True, type=str)
    parser.add_argument("--xml", help="File containing xml file list (default: xml_files.txt)", type=str,
                        default='xml_files.txt')
    parser.add_argument("--source", help="File containing source names (default: source_names.txt)", type=str,
                        default='source_names.txt')
    parser.add_argument("--buffer", help="Ft2 file is expanded backwards and forwards in time by this amount to ensure"
                                         "it covers a time interval >= Ft1 (default: 10000s)", type=float,
                        default=10000)
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

        this_ft2_start = this_ft1_start - args.buffer

        this_ft2_stop = this_ft1_stop + args.buffer

        # cut ft2

        # prepare cut command
        out_ft2 = 'simulated_' + str(this_ft2_start) + '_ft2.fits'

        cmd_line = "ftcopy '%s[SC_DATA][START >= %s && STOP =< %s]' %s copyall=true" \
                   " clobber=true" % (args.in_ft2, this_ft2_start, this_ft2_stop, out_ft2)

        print "\nCreating Ft2 from %s to %s from input (%s of %s Ft2 files)" % (this_ft2_start, this_ft2_stop, i + 1, args.n_days)

        # execute cut
        execute_command(cmd_line)

        # Verify that the command executed and update the header

        with fits.open(out_ft2) as fits_file:

            # Check the start and stop in the binary table
            ft2_starts = fits_file['SC_DATA'].data.field("START")
            ft2_stops = fits_file['SC_DATA'].data.field("STOP")

            print '\nFt2 begins at %s, ends at %s \n' % (ft2_starts.min(), ft2_stops.max())

        print "Simulating Ft1 beginning at %s, ending at %s (%s file)" % (this_ft1_start, this_ft1_stop,
                                                                               numsuf(i + 1))

        # The simulation neeeds an environment variable called SKYMODEL_DIR
        os.environ['SKYMODEL_DIR'] = args.src_dir

        cmd_line = "gtobssim infile=%s " \
                   "srclist=%s " \
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
                   "chatter=5" % (os.path.join(args.src_dir, args.xml), os.path.join(args.src_dir, args.source),
                                  out_ft2, str(int(this_ft1_start)), args.interval, this_ft1_start, int(this_ft1_start))

        # execute simulation
        execute_command(cmd_line)

        # rename output file
        last_ft1 = str(int(this_ft1_start)) + '_events_0000.fits'

        out_ft1 = 'simulated_' + str(int(this_ft1_start)) + '_ft1.fits'

        os.rename(os.path.join(os.getcwd(), last_ft1), os.path.join(os.getcwd(), out_ft1))

        print "\nFt1 begins at %s, ends at %s (%s file)" % (this_ft1_start, this_ft1_stop, numsuf(i + 1))

        # Update the PROC_VER keyword if we are dealing with simulated data
        with fits.open(out_ft1, mode='update') as fits_file:

            if int(fits_file[0].header.get("PROC_VER")) < 100:

                print("Deadling with simulated data. Updating the PROC_VER keyword to '302'... ")

                fits_file[0].header.set("PROC_VER", "302")

        # Verify that the command executed and update the header

        # check that ft1 time range is completely inside ft2
        with fits.open(out_ft2) as fits_file:

            if ft2_starts.min() - this_ft1_start > 0:

                raise RuntimeError("FT2 file starts after the FT1 file")

            if ft2_stops.max() - this_ft1_stop < 0:

                raise RuntimeError("FT2 file stops before the end of the FT1 file")

        # Update the header
        with fits.open(out_ft2, mode='update') as out_ft2:

            out_ft2['SC_DATA'].header.set("TSTART", ft2_starts.min())
            out_ft2['SC_DATA'].header.set("TSTOP", ft2_stops.max())

            out_ft2[0].header.set("TSTART", ft2_starts.min())
            out_ft2[0].header.set("TSTOP", ft2_stops.max())

    print "\nFinished"
