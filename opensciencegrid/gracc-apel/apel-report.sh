#!/bin/bash

function res_rg() {
nlimit=2
rg="NULL"
tmp=`mysql -u root oim -s <<< "select b.name from resource a, resource_group b where a.name='$1' and a.resource_group_id=b.id ;"`
size=${#tmp}
if [ "$size" -gt "$nlimit" ] ; then
    rg=$tmp
else
##  cannot find resource group for this resource
    tmp=`grep $res /home/steige/RGMap | awk '{ print $2 }'`
    size=${#tmp}
    if [ "$size" -gt "$nlimit" ] ; then
	rg=$tmp
    else
##      lookup failed, default resource group to resource name
	rg=$res
    fi
fi
echo $rg
}

## for small core count, node count is 1
nodes=1

if [ $1 ]; then
## finalizing the report from last month
    year=`date --date="last-month" +%Y`
    month=`date --date="last-month" +%m`
    handle="core_final"
else
## process from 1st of month to yesterday
    year=`date --date="yesterday" +%Y`
    month=`date --date="yesterday" +%m`
    handle="core"
fi

## if there was no data newer that "cutoff" days, there is a problem, log it.
cutoff=2.00
rm -f /net/nas01/Public/tmp/problems_${month}_$year

## cutoff, a username shorter than this is ignored
limit=5
limit=-10

## cutoff, stop looking for new users when null result count exceeds this
nlimit=2

nmax=200
zero=0

{
for cores in "1" "8" ; do
   for vo in "atlas" "alice" "cms" "enmr.eu" ; do
       now=`date`
       echo "$now : Starting an $cores core report for $vo">>/var/log/multicore.log

## add header, once per upload
       echo "APEL-summary-job-message: v0.3"

## count users for this month
       nusers=`echo "use gratia ; select count(distinct KeyInfoContent) from JobUsageRecord where ReportableVOName='$vo' and Processors=$cores and Year(EndTime)=$year and Month(EndTime)=$month ;" | mysql --defaults-extra-file=/home/steige/qqq | grep -v count`
    
       now=`date`
       echo "$now : Found $nusers users">>/var/log/multicore.log

       for user_index in `seq 0 $nusers` ; do

	   now=`date`
	   echo "$now : Getting user list">>/var/log/multicore.log
	   user=`echo "use gratia ; select distinct KeyInfoContent from JobUsageRecord where ReportableVOName='$vo' and Processors=$cores and Year(EndTime)=$year and Month(EndTime)=$month limit $user_index,1 ; " | mysql --defaults-extra-file=/home/steige/qqq | grep -v KeyInfoContent`

	   if [ -z "$user" ] ; then
## emplty user name, account as "generic"
	       user="generic $vo user"
	   fi
## find all resources used by this user
	   now=`date`
	   echo "$now : Getting resource list for user $user">>/var/log/multicore.log
	   resources=`echo "use gratia ; select distinct b.ReportedSiteName from JobUsageRecord a , JobUsageRecord_Meta b  where a.dbid=b.dbid and a.ReportableVOName='$vo' and a.Processors=$cores and a.KeyInfoContent='$user' and Month(a.EndTime)=$month and Year(a.EndTime)=$year ; " | mysql --defaults-extra-file=/home/steige/qqq | grep -v Name`
	   size=${#resources}
	   if [ "$size" -gt "$nlimit" ] ; then
## have a non-null resources list, find the resource groups of the resources
	       rgs=`for res in $resources ; do res_rg $res ; done`
	       unique_rgs=`sort -u <<< "${rgs// /$'\n'}"`
	       for unique_rg in $unique_rgs ; do
## initialize use summations here
		   wall=0
		   cpu=0
		   nwall=0
		   ncpu=0
		   njobs=0
		   min_d=`date +%s`
		   max_d=0
		   
		   for resource in $resources ; do
## get the resource group for this resource                                                                                   
		       rg=`res_rg $resource`
		       if [ "${rg}" = "${unique_rg}" ]; then
			
## Normalization factor
## attempt to get a normalization factor from oim
			   nftest=`mysql -u root oim -s <<< "select b.apel_normal_factor from resource a , resource_wlcg b where b.resource_id=a.id and a.name='$resource';"`
## sanity checks on the normalization factor
			   if [ $(echo " $nftest < $nmax && $nftest > $zero" | bc) -eq 1 ] ; then
			       nf=$nftest
			   else
## get the default normalization factor for this resource group
			       nf=`grep ${rg} normal_hepspec | awk '{print $2}'`
			       if [ $(echo " $nf < $nmax && $nf > $zero" | bc) -eq 1 ] ; then
				   now=`date`
				   echo "$now : Warning: Using tabular default normalization factor $nf for $resource">>/var/log/multicore.log
			       else
## normalization factor is not available, use a final, global default
				   nf=12.
				   now=`date`
				   echo "$now : Warning: Using global default normalization factor $nf for $resource">>/var/log/multicore.log
			       fi
			   fi
			
## get summed CPU and Wall time for this user on this resource
			   now=`date`
			   echo "$now : Getting results">>/var/log/multicore.log
			   results=`echo "use gratia ; select sums.norm as WghtdWall , sums.su as CpuUser, sums.ss as CpuSyst, sums.su/sums.norm as UserEff, sums.ss/sums.norm as SystEff, sums.njobs, sums.norm*$nf, sums.su*$nf from (select sum(term.wall)/1 as norm , sum(term.user)/1 as su, sum(term.syst)/1 as ss, count(term.wall) as njobs from (select WallDuration as wall, CpuUserDuration as user, CpuSystemDuration as syst from JobUsageRecord a, JobUsageRecord_Meta b  where a.dbid=b.dbid and Month(a.EndTime)=$month and Year(a.EndTime)=$year and a.Processors=$cores and a.ReportableVOName='$vo' and b.ReportedSiteName='$resource' and a.KeyInfoContent='$user' ) term ) sums; " | mysql --defaults-extra-file=/home/steige/qqq | grep -v WghtdWall`

## find the max and min job end times for the jobs defining usage.
## This is per request from APEL and is different that John W report
			   now=`date`
			   echo "$now : Getting times $resource">>/var/log/multicore.log
			   times=`echo "use gratia ; select min(a.EndTime), max(a.EndTime) from JobUsageRecord a, JobUsageRecord_Meta b  where a.dbid=b.dbid and Month(a.EndTime)=$month and Year(a.EndTime)=$year and a.Processors=$cores and a.ReportableVOName='$vo' and b.ReportedSiteName='$resource' and a.KeyInfoContent='$user'; " | mysql --defaults-extra-file=/home/steige/qqq | grep -v WghtdWall`

			   echo $results | grep NULL >/dev/null
## sum up the results for this user, there may be more than one resource in this resource group
			   if [ "${results/'NULL'}" = "$results" ] ; then
			       now=`date`
			    
			       x=`echo $results | awk '{ print $1 }'`
			       wall=`echo "$wall+$x" | bc`
			    
			       x=`echo $results | awk '{ print $2 }'`
			       cpu=`echo "$cpu+$x" | bc`
			    
			       x=`echo $results | awk '{ print $1 }'`
			       nwall=`echo "$nwall+$x*$nf" | bc`
			    
			       x=`echo $results | awk '{ print $2 }'`
			       ncpu=`echo "$ncpu+$x*$nf" | bc`
			    
			       x=`echo $results | awk '{ print $6 }'`
			       njobs=`echo "$njobs+$x" | bc`
			    
## convert start/end to linux time, find biggest,smallest                                   
                               x=`echo $times | awk '{ print $3, $4}'`
                               x=`date --date="$x" +%s`
                               if [ "$x" -lt "$min_d" ]; then
				   min_d=$x
                               fi
                               x=`echo $times | awk '{ print $5, $6}'`
                               x=`date --date="$x" +%s`
                               if [ "$x" -gt "$max_d" ]; then
				   max_d=$x
                               fi
			   fi
		       fi
		   done
		   now=`date`
		   echo "$now : Writing output of $vo $unique_rg">>/var/log/multicore.log
## output use summation here
		   echo "Site: $unique_rg"
		   echo "VO: $vo"
		   echo "EarliestEndTime: $min_d"
		   echo "LatestEndTime: $max_d"
		   echo "Month: $month"
		   echo "Year: $year"
		   echo "Infrastructure: Gratia-OSG"
		   echo "GlobalUserName: $user"
		   echo "Processors: $cores"
		   echo "NodeCount: $nodes"
## this operation converts the floating point result to integer                                                              
		   x=`echo "scale=0; $wall/1." | bc`
		   echo -n "WallDuration: "
		   echo $x
		   x=`echo "scale=0; $cpu/1." | bc`
		   echo -n "CpuDuration: "
		   echo $x			
		   x=`echo "scale=0; $nwall/1." | bc`
		   echo -n "NormalisedWallDuration: "
		   echo $x		       
		   x=`echo "scale=0; $ncpu/1." | bc`
		   echo -n "NormalisedCpuDuration: "
		   echo $x			
		   echo -n "NumberOfJobs: "
		   echo $njobs
		   echo "%%"
## test for recent reporting
		   {
		   now=`date +%s`
		   age=`echo "$now - $max_d" | bc`
		   x=`echo "scale=3; $age/86400." | bc`
		   if [ $(echo " $x > $cutoff " | bc) -eq 1 ] ; then
		       echo "$unique_rg reported $x days ago, problem"
		   else
		       echo "$unique_rg reported $x days ago, "
		   fi
		   }>>/net/nas01/Public/tmp/problems_${month}_$year
	       done
	   fi
       done
       echo "$now : Finished an $cores core report for $vo">>/var/log/multicore.log
   done
done
}>/net/nas01/Public/tmp/${month}_$year.apel
