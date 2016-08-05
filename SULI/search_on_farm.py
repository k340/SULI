#!/usr/bin/env python

import argparse
import os
import shutil
import glob
import subprocess
from astropy.io import fits


def clean_up():

    # First move out of the workdir
    os.chdir(os.path.expanduser('~'))

    # Now remove the directory
    try:

        shutil.rmtree(workdir)

    except:

        print("Could not remove workdir. Unfortunately I left behind some trash!!")
        raise

    else:

        print("Clean up completed.")


if __name__ == "__main__":

    parser = argparse.ArgumentParser('Wrapper around the search script')

    # Required parameters

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--date', help='date specifying file to load')
    group.add_argument('--inp_fts', help='filenames of ft1 and ft2 input, separated by a comma (ex: foo.ft1,bar.ft2)')

    parser.add_argument("--irf", help="Instrument response function name to be used", type=str, required=True)
    parser.add_argument("--probability", help="Probability of null hypothesis", type=float, default=6.33e-5)
    parser.add_argument("--min_dist", help="Distance above which regions are not considered to overlap", type=float,
                        required=True)
    parser.add_argument("--out_dir", help="Directory which will contain the search results txt file)",
                        required=True, type=str)

    args = parser.parse_args()

    # Check that the output dir already exists
    if not os.path.exists(args.out_dir):

        raise IOError("You need to create the directory %s before running this script" % args.out_dir)

    # First step of a farm job: Stage-in

    # Create a work directory in the local disk on the node

    # This is your unique job ID (a number like 546127)
    unique_id = os.environ.get("PBS_JOBID").split(".")[0]

    workdir = os.path.join('/dev/shm', unique_id)
    print("About to create %s..." % (workdir))

    try:
        os.makedirs(workdir)

    except:

        print("Could not create workdir %s !!!!" % (workdir))
        raise

    else:

        # This will be executed if no exception is raised
        print("Successfully created %s" % (workdir))

    # now you have to go there
    os.chdir(workdir)

    # if using simulated data
    if args.inp_fts:

        # Copy in the input files

        # get names of input files from in_fts
        ft1_name = os.path.abspath(os.path.expandvars(os.path.expanduser(args.inp_fts.rsplit(",", 1)[0])))
        ft2_name = os.path.abspath(os.path.expandvars(os.path.expanduser(args.inp_fts.rsplit(",", 1)[1])))

        # create local files
        local_ft1 = os.path.join(workdir, os.path.basename(ft1_name))
        local_ft2 = os.path.join(workdir, os.path.basename(ft2_name))

        print("Copying %s into %s..." % (ft1_name, local_ft1))
        print("Copying %s into %s..." % (ft2_name, local_ft2))

        # copy them to the files
        shutil.copy(ft1_name, local_ft1)
        shutil.copy(ft2_name, local_ft2)

        # run search

        # use start time of ft1 for outfile name, since ft2 starts early due to buffer
        with fits.open(os.path.join(workdir, os.path.basename(ft1_name))) as ft1:

            file_start = ft1[0].header['TSTART']

        out_name = str(file_start) + '_detections.txt'

        cmd_line = "search_for_transients.py --inp_fts %s --irf %s --probability %s --min_dist %s " \
                   "--out_file %s" % (args.inp_fts, args.irf, args.probability, args.min_dist, out_name)

    # else using real data
    else:

        out_name = str(args.date) + '_detections.txt'

        cmd_line = "search_for_transients.py --date %s --irf %s --probability %s --min_dist %s " \
                   "--out_file %s" % (args.date, args.irf, args.probability, args.min_dist, out_name)

    try:

        # Do search
        print("\n\nAbout to execute command:")
        print(cmd_line)
        print('\n')

        subprocess.check_call(cmd_line, shell=True)

    except:

        print("Cannot execute command: %s" % cmd_line)
        print("Maybe this will help:")
        print("\nContent of directory:\n")

        subprocess.check_call("ls", shell=True)

        print("\nFree space on disk:\n")
        subprocess.check_call("df . -h", shell=True)

    else:

        # Stage-out
        output_files = glob.glob("*_detections.txt")

        if len(output_files) != 1:

            print("\n\nCannot find output files!")

        else:

            # Copy them back

            for filename in output_files:

                shutil.copy(os.path.join(workdir, filename), args.out_dir)

    finally:

        # This is executed in any case, whether an exception have been raised or not
        # I use this so we are sure we are not leaving trash behind even
        # if this job fails

        clean_up()
