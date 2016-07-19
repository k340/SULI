#!/usr/bin/env python

"""This script scans .txt files (from search_for_transients) in a specified directory and returns a list of files
    containing detections. It can also display the contents of all files in the terminal and copy them to another
    folder (optional)."""

import argparse
import numpy as np
import subprocess
from os import listdir
from os.path import join


# execute only if run from command line
if __name__ == "__main__":

    # create parser for this script
    parser = argparse.ArgumentParser('Search input folder')

    # add the arguments needed to the parser
    parser.add_argument("--directory", help="Location of files to be searched", type=str,
                        required=True)
    parser.add_argument("--display", help="Set to [True] to display file contents in terminal", type=bool,
                        default=False)
    parser.add_argument("--mode", help="If Active, will pause and prompt user to continue upon finding a day with more"
                                       "detections than threshold; if Passive, will create text file list of such day"
                                       "files. Active by default", type=str, default='Single')
    parser.add_argument("--threshold", help="Number of detections required for a day to be flagged; 1 by default",
                        type=int, default=1)

    # parse the arguments
    args = parser.parse_args()

    # get list of all .txt files in directory
    files = [f for f in listdir(args.directory) if (str(join(args.directory, f)).endswith('.txt'))]

    # flag all files with events
    interesting_files = []

    for i in range(len(files)):

        active_file_detections = np.recfromtxt(args.directory + '/' + files[i], names=True, usemask=False)

        if len(active_file_detections) >= args.threshold:

            interesting_files.append(files[i])

            if args.mode == 'Active':

                # pause
                pass

            elif args.mode == 'Passive':

                # add files to interesting folder
                cmd = 'mkdir detections'

        # display file contents regardless
        if args.display is True:

            print '%s:' % files[i]
            cmd_line = 'cat %s' % files[i]
            subprocess.check_call(cmd_line, shell=True)

    if len(interesting_files) == 0:

        print '\nNo anomalous detections'

    else:

        print 'The following files have detections:\n'

        for i in range(len(interesting_files)):

            active_file_detections = np.recfromtxt(args.directory + '/' + interesting_files[i], names=True,
                                                   usemask=False)

            print '%s (%s detections)' % (interesting_files[i], len(active_file_detections))
