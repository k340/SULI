#!/usr/bin/env python

import glob
import argparse
import os

import astropy.io.fits as pyfits
from GtApp import GtApp

ft2_file = 'ft2_simulated_283996770-315532800.fits'

if __name__=="__main__":

    parser = argparse.ArgumentParser('Wrapper around the simulation script')

    # Required parameters

    parser.add_argument("--in_ft2", help="Ft2 file containing data to be segmented", required=True, type=str)
    parser.add_argument("--binsize", help="Bin size for the light curve", required=False, default=21600.0, type=float)

    args = parser.parse_args()

    ft2_file = os.path.abspath(os.path.expandvars(os.path.expanduser(args.in_ft2)))

    files = glob.glob("generated_data/*_ft1.fits")

    print("\n\nMaking light curve...")

    with open('ft1_list', 'w+') as f:
        for filename in files:
            f.write("%s\n" % filename)

    gtselect = GtApp('gtselect')
    gtselect['infile'] = '@ft1_list'
    gtselect['outfile'] = 'vela.fits'
    gtselect['ra'] = 128.837917
    gtselect['dec'] = -45.178333
    gtselect['rad'] = 2.0
    gtselect['tmin'] = 'INDEF'
    gtselect['tmax'] = 'INDEF'
    gtselect['emin'] = 100
    gtselect['emax'] = 100000
    gtselect['zmax'] = 180
    gtselect['evclass'] = 128
    gtselect['evtype'] = 3

    gtselect.run()

    data = pyfits.getdata(ft2_file, 'SC_DATA')

    gtbin = GtApp('gtbin')
    gtbin['evfile'] = 'vela.fits'
    gtbin['scfile'] = ft2_file
    gtbin['outfile'] = 'vela_lc.fits'
    gtbin['algorithm'] = 'LC'
    gtbin['tbinalg'] = 'LIN'
    gtbin['tstart'] = data.START.min()
    gtbin['tstop'] = data.STOP.max()
    gtbin['dtime'] = args.binsize
    gtbin.run()

    gtexposure = GtApp('gtexposure')
    gtexposure['infile'] = 'vela_lc.fits'
    gtexposure['scfile'] = ft2_file
    gtexposure['irfs'] = 'CALDB'
    gtexposure['srcmdl'] = 'bnVela_LAT_xmlmodel.xml'
    gtexposure['target'] = "3FGL J0835.3-4510"

    gtexposure.run()
