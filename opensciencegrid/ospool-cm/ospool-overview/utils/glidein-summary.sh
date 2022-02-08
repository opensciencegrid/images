#!/bin/bash

echo
echo "Glidein versions / counts:"
echo
condor_status -af OSG_GLIDEIN_VERSION | sort -n | uniq -c | sort -n -r | perl -ane 'printf("    %-30s %5d\n", $F[1], $F[0])'

echo
echo "Currently contributing sites:"
echo
condor_status -af GLIDEIN_ResourceName | sed 's/ /_/g' | sort -n | uniq -c | sort -n -r | perl -ane 'printf("    %-30s %5d\n", $F[1], $F[0])'

echo
echo "Sites with Singularity detected:"
echo
condor_status -const HAS_SINGULARITY -af GLIDEIN_ResourceName | sed 's/ /_/g' | sort | uniq -c | sort -n -r | perl -ane 'printf("    %-30s %5d\n", $F[1], $F[0])'

echo
echo "Singularity version counts:"
echo
condor_status -const HAS_SINGULARITY -af OSG_SINGULARITY_VERSION | sort | uniq -c

echo
echo "Percentage of sites which has Singularity support:"
echo
SUBSET=`condor_status -const 'HAS_SINGULARITY' -af Name | wc -l`
FULLSET=`condor_status -const 'True' -af Name | wc -l`
perl -e "printf('    %.1f%', ($SUBSET / $FULLSET) * 100);"
echo

echo
echo "OS Breakdown and number of glideins with 0 jobs started:"
echo
echo "              Total 0-jobs"
SAVE_IFS=$IFS
IFS=$(echo -en "\n\b")
for OSGVO_OS_STRING in `condor_status -af OSGVO_OS_STRING | sort | uniq`; do
    COUNT=`condor_status -const "OSGVO_OS_STRING == \"$OSGVO_OS_STRING\"" -af Machine | wc -l`
    ZERO_JOBS=`condor_status -const "JobStarts == 0 && OSGVO_OS_STRING == \"$OSGVO_OS_STRING\"" -af Machine | wc -l`
    printf "  %-10s  %5d  %5d\n" "$OSGVO_OS_STRING" $COUNT $ZERO_JOBS
done 
IFS=$SAVEIFS

echo
echo

