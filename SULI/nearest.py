#!/usr/bin/env python

"""This script takes trigger data from text files with 6 columns,
    obtains dec, ra, tstarts, tstops, and counts,
    and eliminates overlapping regions based on which is more significant,
    returning a text file with the result.
    The assumption is that when overlapping regions trigger simultaneously,
    they are triggering on the same event;
    this script chooses the most significant trigger and removes duplicate detections.
    Significance is determined primarily by number of time bins in a specified area of sky,
    and secondarily by the count rate in the highest count-density bin"""

import numpy as np
from math import *
import argparse


# return distance between centers of regions in inp_list; arg should be region in inp_list
def dist(region1, region2):

    r = acos(sin(region1['dec'])*sin(region2['dec']) + cos(region1['dec'])*cos(region2['dec'])*cos(region1['ra']-region2['ra']))

    return r


# return number of time bins in input region; arg should be region in inp_list
def bins(inp_region):

    # create list of tstarts associated with inp_region
    list_in_string = inp_region['tstarts'].split(",")
    # convert above list into list of floats
    list_in_floats = map(float, list_in_string)

    return len(list_in_floats)


# returns most significant bin and its count rate, given a region as input
def sigbin(inp_region):

    rate_max = 0
    bin_max = 0

    # converts tstarts, etc. entry for i into a readable list
    regstarts = map(float, inp_region['tstarts'].split(","))
    regstops = map(float, inp_region['tstops'].split(","))
    regcounts = map(float, inp_region['counts'].split(","))

    # for each bin in i:
    for k in range(0, bins(inp_region)):

        # if bin has higher count rate than previous highest, set its rate as highest and tag it as brightest bin
        rate = regcounts[k] / (regstops[k] - regstarts[k])
        if rate > rate_max:
            rate_max = rate
            bin_max = k

    return [rate_max, bin_max]


# remove redundant regions
def check_nearest(inp_list, min_dist):

    # list of regions to be returned by function
    regions = inp_list

    # primary iteration counter
    i = 0

    # flag as true to increment counter
    inci = True

    # for each region in inp_list:
    while i in range(len(regions)):

        # sedcondary iteration counter
        j = 1

        # look at each subsequent region j
        while j in range(i + 1, len(regions)):

            # determine if i and j overlap
            if dist(regions[i], regions[j]) <= min_dist:

                # if so, remove the less significant region from output list

                # first see if one has more bins; this means it is more significant
                if bins(regions[j]) != bins(regions[i]):

                    # if i has more bins than j, it is therefore more significant
                    # remove j from list; do not inc j so as not to skip next list element
                    if bins(regions[j]) < bins(regions[i]):

                        regions = regions[regions["name"] != regions.name[j]]

                    # if j has more bins than i
                    # remove i from list; do not inc i so as not to skip next list element, and return to i loop
                    else:

                        regions = regions[regions["name"] != regions.name[i]]
                        inci = False
                        break

                # they have the same number of time bins
                # find the bin in each with highest count rate; make sure highest bins are at the same place in terms of bin order
                # unsure if this accounts for cases where time bins are completely incogruent between regions i and j
                else:

                    # get most significant bin from region i and its rate; do same with j
                    irate = sigbin(regions[i])
                    jrate = sigbin(regions[j])

                    # check if the i bin is same place in terms of bin order as j
                    if irate[1] != jrate[1]:
                        pass
                        # throw error, something weird happened

                    # check if highest rate in i > than in j
                    elif irate[0] >= jrate[0]:

                        # i is more significant than j, remove j from list
                        regions = regions[regions["name"] != regions.name[j]]

                    else:

                        # j is more significant, remove i from list and return to parent loop
                        regions = regions[regions["name"] != regions.name[i]]
                        inci = False
                        break

            else:

                # if nothing was removed from list, inc j to check next region
                j += 1

        # if i wasn't removed, so inci was never set to false, inc i to check next region
        if inci:

            i += 1

        # if i was removed, do not inc i (so as not to skip next region) and reset inci flag
        else:

            inci = True

    # return pruned list
    return regions

# execute only if run from command line
if __name__=="__main__":

    # create parser for this script
    parser = argparse.ArgumentParser('nearest')

    # add the arguments needed to the parser
    parser.add_argument("--inp_list", help = "txt file containing raw data", required  = True, type=str)
    parser.add_argument("--min_dist", help = "distance above which regions are not considered to overlap",
                        type=float, required = True)

    # parse the arguments
    args = parser.parse_args()

    # get input data file from parser and convert to record array
    data = np.recfromtxt(args.inp_list, names=True, usemask=False)

    # check for multiple triggers by same event,
    result = check_nearest(data, args.min_dist)

    import pdb;pdb.set_trace()

    # set name for output file
    name = "trimmed_" + args.inp_list

    # create output file
    with open(name, 'w+') as f:

        # write column headers
        f.write("# %s\n" % (" ".join(result.dtype.names)))

        # write each row of array to file, followed by line break
        for row in result:

            out = " ".join(map(str, row))

            f.write("%s" % out)

            f.write("\n")





