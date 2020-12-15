#!/bin/bash
#
# This file provides a parameterized version of
#  /etc/squid/customize.sh
# that comes from the OSG RPM.
# Note:
#   It will not be overwritten by upgrades.
# This can be further customized by adding pre-awk shell scripts in
#  customize.d/[0-4]*.sh, awk function calls (which may include shell
#  variable substitutions) in customize.d/*.awk, and/or post-awk shell
#  scripts in customize.d/[5-9]*.sh.  The "print" awk function is in
#  customize.d/90-print.awk so begin the filenames of awk function calls
#  with a lower number than that if you want them to run before the print
#  or a higher number if you want them after the print.  Generally only
#  "insertline" function calls makes sense after the print, if you want
#  to insert after the given line instead of before.
# See customhelps.awk for information on predefined edit functions.
# Quotes in the awk sources have to protected from bash.
#

cd `dirname $0`/customize.d

for f in [0-4]*.sh; do
    if [ -f "$f" ]; then
        . $f
    fi
done


awk --file ../customhelps.awk --source "{
$(for f in *.awk; do eval "echo \"$(cat $f)\""; done)
}"

for f in [5-9]*.sh; do
    if [ -f "$f" ]; then
        . $f
    fi
done
