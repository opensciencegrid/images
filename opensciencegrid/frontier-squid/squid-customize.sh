#!/bin/bash
#
# This file provides a parameterized version of
#  /etc/squid/customize.sh
# that comes from the OSG RPM.
# Note:
#   It will not be overwritten by upgrades.
# This can be further customized by adding pre-awk shell scripts in
#  customize.d/[0-4]*.sh, awk function calls in customize.d/*.awk,
#  and/or post-awk shell scripts in customize.d/[5-9]*.sh.  Awk files
#  may include shell variable substitutions, but the files are
#  surrounded by single quotes so put a close single quote ahead of a
#  variable and an open single quote after the variable.  The "print"
#  awk function call is in customize.d/90-print.awk so begin the
#  filenames of awk function calls with a lower number than that if you
#  want them to run before the print or a higher number if you want them
#  after the print.  Generally only "insertline" function calls make
#  sense after the print, if you want to insert after the given line
#  instead of before.
# See customhelps.awk for information on predefined edit functions.
#

cd `dirname $0`/customize.d

for f in [0-4]*.sh; do
    if [ -f "$f" ]; then
        . $f
    fi
done


awk --file ../customhelps.awk --source "{
$(for f in *.awk; do eval "echo '$(cat $f)'"; done)
}"

for f in [5-9]*.sh; do
    if [ -f "$f" ]; then
        . $f
    fi
done
