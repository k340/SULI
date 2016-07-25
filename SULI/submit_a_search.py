#!/usr/bin/env python

import numpy as np
import argparse
import os
import time
import sys

from SULI import which
from SULI.execute_command import execute_command
from SULI.work_within_directory import work_within_directory
from astropy.io import fits

if __name__ == "__main__":

    parser = argparse.ArgumentParser('Submit transient search to the farm at Stanford')

    # add the arguments needed to the parser
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--date', help='date specifying file to load')
    group.add_argument("--src_dir", help="Directory containing input data to be searched", type=str)

    parser.add_argument("--irf", help="Instrument response function name to be used", type=str, required=True)
    parser.add_argument("--probability", help="Probability of null hypothesis", type=float, required=True)
    parser.add_argument("--min_dist", help="Distance above which regions are not considered to overlap", type=float,
                        required=True)

    parser.add_argument("--res_dir", help="Directory where to put the results and logs for the search",
                        required=False, type=str, default=os.getcwd())
    parser.add_argument("--job_size", help="Number of jobs to submit at a time", required=False, type=int, default=20)

    parser.add_argument('--test', dest='test_run', action='store_true')
    parser.set_defaults(test_run=False)

    # parse the arguments
    args = parser.parse_args()

    # get output directory from parser
    res_dir = os.path.abspath(os.path.expandvars(os.path.expanduser(args.res_dir)))

    # Check that the output directory exists
    if not os.path.exists(res_dir):

        raise RuntimeError("Directory %s does not exist" % res_dir)

    # get src directory from parser
    src_dir = os.path.abspath(os.path.expandvars(os.path.expanduser(args.src_dir)))

    # Check that the simulation directory exists
    if not os.path.exists(src_dir):

        raise RuntimeError("Directory %s does not exist" % src_dir)

    # Go to output directory
    with work_within_directory(res_dir):

        # Create logs directory if it does not exist
        if not os.path.exists('logs'):

            os.mkdir('logs')

        # Create generated_data directory if it does not exist, and get number of files in the directory
        if not os.path.exists('generated_data'):

            os.mkdir('generated_data')

        DIR = './generated_data'
        num_res_files = len([results for results in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, results))])

        # Generate universal command line parameters
        log_path = os.path.abspath('logs')
        out_path = os.path.abspath('generated_data')
        exe_path = which.which('search_on_farm.py')

        # if using simulated data:
        if args.src_dir:

            # get list of ft1 files
            ft1_files = [f for f in os.listdir(src_dir) if (str(os.path.join(src_dir, f)).endswith(('ft1.fits',
                                                                                                    'ft1.fit')))]
            # (is basically glob, should be changed to glob at some point)

            # get list of ft2 files
            ft2_files = [f for f in os.listdir(src_dir) if (str(os.path.join(src_dir, f)).endswith(('ft2.fits',
                                                                                                    'ft2.fit')))]

            # sort them
            def ft_sort(in_list):

                out_list = in_list.split("_")[1]

                return float(out_list)

            ft1_files = sorted(ft1_files, key=ft_sort)
            ft2_files = sorted(ft2_files, key=ft_sort)

            print '\nFound %s ft1 files\nFound %s ft2 files\n' % (len(ft1_files), len(ft2_files))

            # make sure each ft1/ft2 is part of a pair
            if len(ft1_files) != len(ft2_files):

                # determine which type there is more of for error msg
                if len(ft1_files) > len(ft2_files):

                    x = 'ft1 files'
                    y = 'ft2 files'

                else:

                    x = 'ft2 files'
                    y = 'ft1 files'

                raise RuntimeError('There are more %s than %s' % (x, y))

            # make sure pairs match
            for i in range(len(ft1_files)):

                with fits.open(os.path.join(src_dir, ft1_files[i])) as fits_file:

                    # Check the start and stop in the binary table
                    ft1_times = fits_file['EVENTS'].data.field("TIME")
                    ft1_starts = fits_file['GTI'].data.field("START")
                    ft1_stops = fits_file['GTI'].data.field("STOP")

                with fits.open(os.path.join(src_dir, ft2_files[i])) as fits_file:

                    # Check the start and stop in the binary table
                    ft2_starts = fits_file['SC_DATA'].data.field("START")
                    ft2_stops = fits_file['SC_DATA'].data.field("STOP")

                if ft2_starts.min() - min(ft1_starts.min(), ft1_times.min()) > 0:

                    raise RuntimeError("Mismatch in ft pair %s (FT2 file starts after the start of the FT1 file)" % i)

                if ft2_stops.max() - max(ft1_stops.max(), ft1_stops.max()) < 0:

                    raise RuntimeError("Mismatch in ft pair %s (FT2 file stops before the end of the FT1 file)" % i)

            # generate command line
            def sim_cmd_line(ft1, ft2, jobid):

                this_cmd_line = "qsub -l vmem=30gb -o %s/%s.out -e %s/%s.err -V -F '--inp_fts %s,%s --irf %s " \
                                "--probability %s --min_dist %s --out_dir %s' %s" % (log_path, jobid, log_path,
                                                                                     jobid, ft1, ft2, args.irf,
                                                                                     args.probability, args.min_dist,
                                                                                     out_path, exe_path)
                return this_cmd_line

            # iterate over input directory, calling search on each pair of fits
            for i in range(len(ft1_files)):

                this_ft1 = src_dir + '/' + ft1_files[i]
                this_ft2 = src_dir + '/' + ft2_files[i]
                this_id = ft1_files[i]

                cmd_line = sim_cmd_line(this_ft1, this_ft2, this_id)

                if not args.test_run:

                    execute_command(cmd_line)

                # don't spam the farm; if more than [jobsize] jobs have been submitted,
                # wait until they finish to submit more
                if (i + 1) % args.job_size == 0:

                    # check res_dir every 10s for new results

                    # while the current number of results is not i+1 more than the initial number
                    # i.e., while the number of new files hasn't caught up to i + 1

                    num_fin = len([results for results in os.listdir(DIR) if os.path.isfile(os.path.join(DIR,
                                                                                                         results))])
                    sleep_count = 0
                    while num_fin - num_res_files != i + 1:

                        # sleep for 10s
                        time.sleep(10)
                        sleep_count += 1

                        # update num_fin for any finished jobs
                        num_fin = len([results for results in os.listdir(DIR) if os.path.isfile(os.path.join(DIR,
                                                                                                             results))])
                        print "%s ouf of %s jobs in this pass finished." % (num_fin - num_res_files, args.job_size)

                        # if it is taking to long, prompt to continue
                        if sleep_count >= 60:

                            def continue_prompt(inp_string):

                                sys.stdout.write(inp_string)
                                sys.stdout.write("Job is taking longer than usual. Abort? [y/n]")
                                inp = raw_input().lower()

                                if inp == 'y':

                                    raise RuntimeError("Farm took too long to respond. Aborting search.")

                                elif inp =='n':

                                    return 0

                                else:

                                    continue_prompt('Invalid prompt\n')

                            sleep_count = continue_prompt('\n')

        else:

            def rl_cmd_line(start):

                this_cmd_line = "qsub -l vmem=10gb -o %s/%s.out -e %s/%s.err -V -F '--date %s --irf %s " \
                                "--probability %s --min_dist %s --out_dir %s' %s" % (log_path, start, log_path,
                                                                                     start, start, args.irf,
                                                                                     args.probability, args.min_dist,
                                                                                     out_path, exe_path)
                return this_cmd_line

            # A year of Fermi data

            dates = np.arange(args.date, args.date + (365.0 * 86400.0), 86400.0)

            for this_tstart in dates:

                cmd_line = rl_cmd_line(this_tstart)

                if not args.test_run:

                    execute_command(cmd_line)
