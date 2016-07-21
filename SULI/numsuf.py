
# appends appropriate suffix to an integer
def numsuf(n):

    if (n % 10 == 1) & (n % 100 != 11):

        th = 'st'

    elif (n % 10 == 2) & (n % 100 != 12):

        th = 'nd'

    elif (n  % 10 == 3) & (n % 100 != 13):

        th = 'rd'

    else:

        th = 'th'

    return "%s%s" % (n, th)