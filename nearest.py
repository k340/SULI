
"""takes an array of regions with dec, ra, tstart, tstop, count, roi, and eliminates overlapping regions based on which is more significant"""

#returns distance between centers of input regions from inp_list
def dist(region1, region2):

    r = abs(region2-region1) #replace with actual math

    return r

#returns number of time bins in input region; arg should be region in inp_list
def bins(inp_region):

    num = 0 #replace with bin number

    return num

#returns number of counts in bin divided by bin width (time); arg should be a bin of region in inp_list
def rate(inp_bin):

    cpt = inp_bin['counts'] / (inp_bin['tStop'] - inp_bin['tStart'])

    return cpt

#remove redundant regions
def elim_mult_trig(inp_list, min_dist):

    regions = inp_list # list of regions to be returned by function

    dec_i = False # used to shift i backwards in loop
    dec_j = False # used to shift j backwards in loop

    for i in range(0, len(regions)): # for each region in inp_list

        # steps i back by one so as not to skip regions if one was removed in previous loop iteration
        if dec_i:

            i -= 1
            dec_i = False

        for j in range(i, len(regions)): # look at each subsequent region j

            # steps j back by one so as not to skip regions if one was removed in previous loop iteration
            if dec_j:

                j -= 1
                dec_j = False

            if dist(regions[i], regions[j]) <= min_dist: # determine if i and j overlap

                    # if so, remove the less significant region from output list

                    #first see if one has more bins; this means it is more significant
                    if bins(regions[j]) != bins(regions[i]):

                        # if i has more bins than j, and is therefore more significant, remove j from list and dec j so as not to skip next list element
                        if bins(regions[j]) < bins(regions[i]):

                            regions.pop(j)
                            dec_j = True

                        # if j has more bins than i, and is therefore more significant, remove i from list, dec i so as not to skip next list element, and return to parent loop
                        else:

                            regions.pop(i)
                            dec_i = True
                            break

                    # if they have the same number of time bins, find the bin in each with highest count rate; make sure highest bins are at the same place in terms of bin order
                    # I am unsure if this accounts for cases where time bins are completely incogruent between regions i and j
                    else:

                        irate_max = 0
                        ibin_max = 0
                        jrate_max = 0
                        jbin_max = 0

                        for k in range(0, len(regions[i])): # for each bin in i

                            # if bin has higher count rate than previous highest, set its rate as highest and tag it as brightest bin
                            if rate(regions[i][k]) > irate_max:

                                irate_max = rate(regions[i][k])
                                ibin_max = k

                        # do same with region j
                        for k in range(0, len(regions[j])):

                            if rate(regions[j][k]) > jrate_max:

                                jrate_max = rate(regions[i][k])
                                jbin_max = k

                        if ibin_max != jbin_max:

                                pass
                                # throw error, something weird happened

                        elif irate_max >= jrate_max:

                            # i is more significant than j, remove j from list and dec j so as not to skip next list element
                            regions.pop(j)
                            dec_j = True

                        else:

                            # j is more significant, remove i from list, dec i, and return to parent loop
                            regions.pop(i)
                            dec_i = True
                            break
            else:

                pass

        return regions

