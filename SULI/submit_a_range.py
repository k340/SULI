#!/usr/bin/env python

import numpy as np
import subprocess
import argparse
import os
import astropy.io.fits as pyfits

from SULI import which
from SULI.work_within_directory import work_within_directory

if __name__=="__main__":

    parser = argparse.ArgumentParser(
        'Submit simulation to the farm at Stanford')

    # add the arguments needed to the parser
    parser.add_argument("--in_ft2", help="Ft2 file containing data to be segmented", required=True, type=str)

    parser.add_argument("--src_dir", help="Directory containing input data for the simulation",
                        required=True, type=str)

    parser.add_argument("--res_dir", help="Directory where to put the results and logs for the simulation",
                        required=False, type=str, default=os.getcwd())

    parser.add_argument('--test', dest='test_run', action='store_true')
    parser.set_defaults(test_run=False)

    # parse the arguments
    args = parser.parse_args()

    # Check that the output directory exists

    res_dir = os.path.abspath(os.path.expandvars(os.path.expanduser(args.res_dir)))

    if not os.path.exists(res_dir):

        raise RuntimeError("Directory %s does not exists" % res_dir)

    # Check that the simulation directory exists

    src_dir = os.path.abspath(os.path.expandvars(os.path.expanduser(args.src_dir)))

    if not os.path.exists(src_dir):

        raise RuntimeError("Directory %s does not exists" % src_dir)

    # Go there

    with work_within_directory(res_dir):

        # Create logs directory if does not exists
        if not os.path.exists('logs'):

            os.mkdir('logs')

        # Create generated_data directory, if does not exist
        if not os.path.exists('generated_data'):

            os.mkdir('generated_data')


        # Read in the FT2 file

        ft2_path = os.path.abspath(os.path.expandvars(os.path.expanduser(args.in_ft2)))

        data = pyfits.getdata(ft2_path, "SC_DATA")

        ft2_tstart = data.START.min()

        # Generate the command line

        log_path = os.path.abspath('logs')
        out_path = os.path.abspath('generated_data')

        # Find executable
        exe_path = which.which('simulate_in_the_farm.py')

        def get_cmd_line(this_tstart):

            cmd_line = "qsub -l vmem=10gb -o %s/%s.out -e %s/%s.err -V -F '--tstart %s --in_ft2 %s " \
                       "--src_dir %s --out_dir %s' %s" %(log_path, this_tstart, log_path, this_tstart,
                                                         this_tstart, ft2_path, src_dir, out_path, exe_path)

            return cmd_line

        # A year

        tstarts = np.arange(ft2_tstart, ft2_tstart + (365.0 * 86400.0), 86400.0)

        for this_tstart in tstarts:

            this_cmd_line = get_cmd_line(this_tstart)

            print(this_cmd_line)

            if not args.test_run:

                subprocess.check_call(this_cmd_line, shell=True)
