#!/usr/bin/env python

import numpy as np
import subprocess

if __name__=="__main__":

    tstart = 239557420.0

    cmd_line = "qsub -l vmem=10gb  -V -F '--tstart %s " \
               "--in_ft2 /home/suli_students/suli_kelin/simulation/ft2_1_year.fits " \
               "--src_dir /home/suli_students/suli_kelin/simulation_input/3FGLSkyPass8R2 " \
               "--out_dir /home/suli_students/suli_kelin/simulation/generated_data' " \
               "/home/suli_students/suli_kelin/LAT_transient_search/SULI/SULI/simulate_in_the_farm.py"

    # A year

    tstarts = np.arange(tstart, tstart + (365.0*86400.0), 86400.0)

    for tstart in tstarts:

        this_cmd_line = cmd_line % tstart

        print(this_cmd_line)

        subprocess.check_call(cmd_line, shell=True)
