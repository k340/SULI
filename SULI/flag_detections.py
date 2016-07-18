#!/usr/bin/env python

"""This script scans .txt files (from search_for_transients) in a specified directory and returns a list of files
    containing detections. It can also display the contents of all files in the terminal (optional)"""

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
    parser.add_argument("--display", help="Set to [True] to display file contents in terminal", type=bool)

    # parse the arguments
    args = parser.parse_args(['--directory', '/media/sf_VM_shared/tests/flag_tests', '--display', 'True'])

    # get list of all .txt files in directory
    files = [f for f in listdir(args.directory) if (str(join(args.directory, f)).endswith('.txt'))]

    # flag all files with events
    interesting_files = []

    for i in range(len(files)):

        active_file_detections = np.recfromtxt(args.directory + '/' + files[i], names=True, usemask=False)

        if len(active_file_detections) != 0:
            interesting_files.append(files[i])

        # display file contents regardless
        if args.display is True:
            cmd_line = 'cat %s' % files[i]
            subprocess.check_call(cmd_line, shell=True)

    print 'The following files have detections:\n'

    for i in range(len(interesting_files)):
        active_file_detections = np.recfromtxt(args.directory + '/' + interesting_files[i], names=True, usemask=False)
        print '%s (%s detections)' % (interesting_files[i], len(active_file_detections))
