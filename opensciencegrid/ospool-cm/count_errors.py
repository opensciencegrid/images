#!/usr/bin/python3

import sys
import time

# container start time is in epoch format
starttime = time.gmtime(int(sys.argv[1]))

error_count = 0
for line in sys.stdin:
    # split the line into (year, time, everything else)
    split_line = line.split(" ", 2)
    try:
        # parse the timestamp -- should look like "08/01/23 11:47:36"
        string_ = "{} {}".format(*split_line[0:2])
        format_ = "%m/%d/%y %H:%M:%S"
        linetime = time.strptime(string_, format_)
    except (TypeError, ValueError):
        # could not parse it; skip this line
        continue
    if linetime < starttime:
        # this happened before container startup, skip it
        continue
    if "ERROR: AUTHENTICATE" in line:
        error_count += 1

print(error_count)

