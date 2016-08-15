#!/usr/bin/env python

import argparse
import os
import time
import calendar

from SULI import which
from SULI.execute_command import execute_command
from SULI.work_within_directory import work_within_directory
from astropy.io import fits
from subprocess import check_output


if __name__ == "__main__":

    parser = argparse.ArgumentParser('Submit transient search to the farm at Stanford')

    # add the arguments needed to the parser
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--start', help="Date (yyyy-mm-ddThh:mm:ss) from which a year of real data will be searched",
                       type=str)
    group.add_argument('--dates', help='Name of txt file containing dates to load real data from', type=str)
    group.add_argument('--date', help='Date of real data that will be searched', type=str)
    group.add_argument("--src_dir", help="Directory containing simulated data to be searched", type=str)

    parser.add_argument("--irf", help="Instrument response function name to be used", type=str, required=True)
    parser.add_argument("--probability", help="Probability of null hypothesis", type=float, default=6.33e-5)
    parser.add_argument("--min_dist", help="Distance above which regions are not considered to overlap", type=float,
                        required=True)

    parser.add_argument("--res_dir", help="Directory where to put the results and logs for the search",
                        required=False, type=str, default=os.getcwd())
    parser.add_argument("--job_size", help="Number of jobs to submit at a time", required=False, type=int, default=20)
    parser.add_argument("--last_job", help="Integer specifying the last job submitted in this folder/year",
                        required=False, type=int, default=0)
    parser.add_argument('--test', dest='test_run', action='store_true')
    parser.set_defaults(test_run=False)

    # parse the arguments
    args = parser.parse_args()

    # get output directory from parser
    res_dir = os.path.abspath(os.path.expandvars(os.path.expanduser(args.res_dir)))

    # Check that the output directory exists
    if not os.path.exists(res_dir):

        raise RuntimeError("Directory %s does not exist" % res_dir)

    # Go to output directory
    with work_within_directory(res_dir):

        # Create logs directory if it does not exist
        if not os.path.exists('logs'):

            os.mkdir('logs')

        # Create generated_data directory if it does not exist, and get number of files in the directory if it does
        if not os.path.exists('generated_data'):

            os.mkdir('generated_data')

        DIR = './generated_data'
        num_res_files = len([results for results in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, results))])

        # Generate universal command line parameters
        log_path = os.path.abspath('logs')
        out_path = os.path.abspath('generated_data')
        exe_path = which.which('search_on_farm.py')

        # loop-staggering function for bulk submissions to farm

        def safe_run(var, fail_track):

            # don't spam the farm; if more than [jobsize] jobs have been submitted,
            # wait until they finish to submit more
            if (var + 1) % args.job_size == 0:


                # number of files in directory at beginning
                num_fin = len([res for res in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, res))])

                # tracking variables
                sleep_count = 0
                failed = False

                # while the current number of results is not i+1 more than the initial number,
                # i.e., while the number of new files hasn't caught up to i + 1
                # check res_dir every 30s for new results
                while (num_fin - num_res_files) < (var + 1 - args.last_job) and failed is False:

                    # sleep for 30s
                    time.sleep(30)
                    sleep_count += 1

                    # update num_fin for any finished jobs
                    num_fin = len(
                        [res for res in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, res))])

                    # Job status for anyone watching
                    print "%s ouf of %s " \
                          "jobs in this pass finished." % ((num_fin - num_res_files) % args.job_size,
                                                           args.job_size)

                    print "%s results in gen data (%s at start)" % (num_fin, num_res_files)

                    print "i = %s\n " \
                          "finished - initial = %s\n" \
                          "i+1-lastjob = %s\n" % (var, num_fin - num_res_files, var + 1 - args.last_job)

                    # some jobs may possibly fail
                    # if script has been on same batch for 15 min, check for job failures
                    if sleep_count >= 30:

                        # get logs
                        log = './logs'
                        log_list = [out for out in os.listdir(log) if (str(os.path.join(log, out)).endswith('.out'))]
                        num_out = len(log_list)

                        # get (your) jobs currently running on farm

                        # farm status
                        qstat = check_output("qstat", shell=True).split("\n")

                        # list of jobs
                        mod_qstat = []
                        for k in range(2, len(qstat) - 1):

                            mod_qstat.append(qstat[i].split("   ", 2))

                        # list of your jobs
                        my_jobs = []
                        for k in range(len(mod_qstat)):

                            if mod_qstat[k][1] == '  ...ch_on_farm.py suli_students':

                                my_jobs.append(mod_qstat[k])

                        # error checks:
                        #   1) if log file has not been created for submitted jobs
                        #   2) if job is not on farm but there is no output file
                        #   3) if logs contain non-0 exit status

                        # 1)
                        if num_out != var + 1:

                            print('Job(s) appear to have died (Missing Log File)')
                            failed = True
                            fail_track.append(var)

                        # 2)
                        elif (num_fin - num_res_files) < (var + 1 - args.last_job) - len(my_jobs):

                            print('Job(s) appears to have failed (Fewer jobs on farm than expected)')
                            failed = True
                            fail_track.append(var)

                        # 3)
                        else:

                            for k in range(var - args.job_size, var + 1):

                                if 0 == 1: # 'non-zero exit status' in open(str(os.path.join(log, out)).read()):

                                    print('Job(s) appears to have failed (Non-zero exit status in log file)')
                                    failed = True
                                    fail_track.append(var)

        # if using simulated data:
        if args.src_dir:

            # get src directory from parser
            src_dir = os.path.abspath(os.path.expandvars(os.path.expanduser(args.src_dir)))

            # Check that the src directory exists
            if not os.path.exists(src_dir):

                raise RuntimeError("Directory %s does not exist" % src_dir)

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
            fails = []
            for i in range(args.last_job, len(ft1_files)):

                this_ft1 = src_dir + '/' + ft1_files[i]
                this_ft2 = src_dir + '/' + ft2_files[i]
                this_id = ft1_files[i]

                cmd_line = sim_cmd_line(this_ft1, this_ft2, this_id)
                if not args.test_run:

                    print "\nDay %s:" % (i + 1)
                    execute_command(cmd_line)

                    safe_run(i, fails)

                    if len(fails) >= 10:

                        pass
                        # raise RuntimeError('Too Many Jobs Have Failed')
                        # this is not to be implimented until more robust error detection is introduced
                        # plan is to check contents of log files rather than existence

        # else using real data
        else:

            def rl_cmd_line(start):

                this_cmd_line = "qsub -l vmem=30gb -o %s/%s.out -e %s/%s.err -V -F '--date %s --irf %s " \
                                "--probability %s --min_dist %s --out_dir %s' %s" % (log_path, start, log_path,
                                                                                     start, start, args.irf,
                                                                                     args.probability, args.min_dist,
                                                                                     out_path, exe_path)
                return this_cmd_line

            # single day
            if args.date:

                cmd_line = rl_cmd_line(args.date)

                if not args.test_run:

                    execute_command(cmd_line)

            # A list of dates
            elif args.dates:

                # get dates from file as a list
                dates = [line.rstrip('\n') for line in open(args.dates)]

                # iterate over dates, searching each
                fails = []
                for i in range(len(dates)):

                    cmd_line = rl_cmd_line(dates[i])

                    if not args.test_run:

                        execute_command(cmd_line)

                        safe_run(i, fails)

                        if len(fails) >= 10:
                            pass
                            # raise RuntimeError('Too Many Jobs Have Failed')

            # a year of data
            else:

                date_list = []
                year_length = 365
                num_days = 31

                # for each month, determine number of days in month,
                # then add the string representation of that date in month to date_list
                for m in range(12):

                    # if February
                    if m == 1:

                        # get year from start date, cast as int, check if leap year
                        if calendar.isleap(int(args.start.split("-", 1)[0])):

                            year_length = 366

                            num_days = 29

                        else:

                            num_days = 28

                    # if month has 30 days
                    elif m == 3 or m == 5 or m == 8 or m == 10:

                        num_days = 30

                    # if normal month
                    else:

                        num_days = 31

                    # for each day in month, construct date string and add it to date_list
                    for d in range(num_days):

                        if (m + 1) >= 10:

                            this_month = str(m + 1)

                        else:

                            this_month = "0%s" % str(m + 1)

                        if (d + 1) >= 10:

                            this_day = str(d + 1)

                        else:

                            this_day = "0%s" % str(d + 1)

                        this_date = "%s-%s-%sT00:00:00" % (args.start.split("-", 1)[0], this_month, this_day)

                        date_list.append(this_date)

                # iterate over year, searching each day
                fails = []
                for i in range(args.last_job, year_length):

                    cmd_line = rl_cmd_line(date_list[i])

                    if not args.test_run:

                        print "\nDay %s:" % (i + 1)
                        execute_command(cmd_line)

                        safe_run(i, fails)

                        if len(fails) >= 10:
                            pass
                            # raise RuntimeError('Too Many Jobs Have Failed')
