#!/usr/bin/env python

"""This script checks .txt files (from search_for_transients) in a specified directory and returns a list of files
    containing detections. It can also display the contents of all files in the terminal and copy them to another
    folder (optional)."""

import argparse
import numpy as np
import subprocess
import os
from os import listdir
from os.path import join


# execute only if run from command line
if __name__ == "__main__":

    # create parser for this script
    parser = argparse.ArgumentParser('Search input folder')

    # add the arguments needed to the parser
    parser.add_argument("--directory", help="Location of files to be searched", type=str,
                        default=os.getcwd())
    parser.add_argument("--display", help="Set to [True] to display file contents in terminal", type=bool,
                        default=False)
    parser.add_argument("--out_file", help="If defined, name of txt file with path/name of files with detections",
                        type=str, default='')
    parser.add_argument("--threshold", help="Number of detections required for a day to be flagged; 1 by default",
                        type=int, default=1)

    # parse the arguments
    args = parser.parse_args()

    # get list of all .txt files in directory
    files = [f for f in listdir(args.directory) if (str(join(args.directory, f)).endswith('_detections.txt'))]

    # flag all files with events
    interesting_files = []

    # for all day files
    for i in range(len(files)):

        # get the contents of file
        active_file_detections = np.recfromtxt(args.directory + '/' + files[i], names=True, usemask=False)

        # if it is not empty, add to list of notable files
        if active_file_detections.size >= args.threshold:

            interesting_files.append(files[i])

        # display file contents regardless, if specified
        if args.display is True:

            print '\n%s:' % files[i]
            cmd_line = 'cat %s' % files[i]
            subprocess.check_call(cmd_line, shell=True)

    if len(interesting_files) == 0:

        print '\nNo anomalous detections'

    else:

        print 'The following files have detections:\n'

        with open(args.out_file + '.txt', 'w+') as f:

            for i in range(len(interesting_files)):

                # get list of detections in interesting_files[i] and print its length

                active_file_detections = np.recfromtxt(args.directory + '/' + interesting_files[i], names=True,
                                                       usemask=False)
                print '%s (%s detections)' % (interesting_files[i], active_file_detections.size)

                # and write to out_file if specified
                if args.out_file:

                    f.write("%s\n" % (interesting_files[i]))
