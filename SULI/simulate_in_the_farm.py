#!/usr/bin/env python

import argparse
import os
import shutil
import glob
import subprocess


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

    parser = argparse.ArgumentParser('Wrapper around the simulation script')

    # Required parameters

    parser.add_argument("--tstart", help="TSTART for ft1 simulation", required=True, type=float)
    parser.add_argument("--in_ft2", help="Ft2 file containing data to be segmented", required=True, type=str)
    parser.add_argument("--src_dir", help="Directory containing the input files for the simulation "
                                          "(XML file, spectra, source names and so on...)", required=True, type=str)

    parser.add_argument("--out_dir", help="Directory which will contain the results of the simulation "
                                          "(ft1 and ft2 file)", required=True, type=str)

    # Optional parameters

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

    args = parser.parse_args()

    # Check that the output dir already exists
    if not os.path.exists(args.out_dir):

        raise IOError("You need to create the directory %s before running this script" % args.out_dir)

    # First step of a farm job: Stage-in

    # Create a work directory in the local disk on the node

    # This is your unique job ID (a number like 546127)
    unique_id = os.environ.get("PBS_JOBID").split(".")[0]

    # os.path.join joins two path in a system-independent way
    workdir = os.path.join('/dev/shm', unique_id)

    # Now create the workdir
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

    # Copy in the input files

    local_ft2 = os.path.join(workdir, os.path.basename(args.in_ft2))

    print("Copying %s into %s..." % (args.in_ft2, local_ft2))

    shutil.copy(args.in_ft2, local_ft2)

    src_dir_basename = os.path.split(args.src_dir)[-1]

    local_src_dir = os.path.join(workdir, src_dir_basename)

    print("Copying %s into %s..." % (args.src_dir, local_src_dir))

    shutil.copytree(args.src_dir, local_src_dir)

    cmd_line = "sim_day_fits.py --tstart %s --in_ft2 %s --src_dir %s --xml %s --source %s --buffer %s " \
               "--n_days %s --evclass %s --zmax %s --interval %s" % (args.tstart, local_ft2, local_src_dir,
                                                                     args.xml, args.source, args.buffer,
                                                                     args.n_days, args.evclass, args.zmax,
                                                                     args.interval)

    try:

        # Do whathever
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
        output_files = glob.glob("simulated_*_ft?.fits")

        if len(output_files) != 2:

            print("\n\nCannot find output files!")

            clean_up()

        else:

            # Copy them back

            for filename in output_files:

                shutil.copy(os.path.join(workdir, filename), args.out_dir)

    finally:

        # This is executed in any case, whether an exception have been raised or not
        # I use this so we are sure we are not leaving trash behind even
        # if this job fails

        clean_up()

