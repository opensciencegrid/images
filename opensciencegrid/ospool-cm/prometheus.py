#!/usr/bin/python3

'''
Prometheus monitor for the OSPool
'''

import htcondor
import re
import sys
import time

from pprint import pprint
from prometheus_client import start_http_server, Gauge, Counter

# resource metrics
ospool_total_cpus_count = Gauge("ospool_total_cpus_count", "Total CPUs", ["resource_name"])
ospool_claimed_cpus_count = Gauge("ospool_claimed_cpus_count", "Claimed CPUs", ["resource_name"])
ospool_idle_retirement_cpus_count = Gauge("ospool_idle_retirement_cpus_count", "Idle CPUs due to retirement", ["resource_name"])
ospool_idle_memstarvation_cpus_count = Gauge("ospool_idle_memstarvation_cpus_count", "Idle CPUs due to starvation", ["resource_name"])
ospool_idle_other_cpus_count = Gauge("ospool_idle_other_cpus_count", "Idle CPUs due to other reasons", ["resource_name"])

# submitter metrics
ospool_submitter_idle_jobs_count = Gauge("ospool_submitter_idle_jobs_count", "Submitter idle jobs", ["submitter", "schedd"])
ospool_submitter_running_jobs_count = Gauge("ospool_submitter_running_jobs_count", "Submitter running jobs", ["submitter", "schedd"])
ospool_submitter_held_jobs_count = Gauge("ospool_submitter_held_jobs_count", "Submitter held jobs", ["submitter", "schedd"])

def cm_resources_info(collector):
    '''
    Discover the sites, and then query for specifics per site.
    Can we do this in a single query?
    '''
    resources = {}

    ads = collector.query(ad_type=htcondor.AdTypes.Startd,
                          constraint="True",
                          projection=["GLIDEIN_ResourceName"])
    for ad in ads:
        if ad["GLIDEIN_ResourceName"] not in resources:
            resources[ad["GLIDEIN_ResourceName"]] = {}

    for resource, data in resources.items():
        
        # total cpus
        total_cpus = 0
        ads = collector.query(ad_type=htcondor.AdTypes.Startd,
                              constraint=f"GLIDEIN_ResourceName == \"{resource}\"",
                              projection=["CPUs"])
        for ad in ads:
            total_cpus += int(ad["CPUs"])
        ospool_total_cpus_count.labels(resource).set(total_cpus)
        
        # claimed cpus
        claimed_cpus = 0
        ads = collector.query(ad_type=htcondor.AdTypes.Startd,
                              constraint=f"GLIDEIN_ResourceName == \"{resource}\" && State != \"Unclaimed\"",
                              projection=["CPUs"])
        for ad in ads:
            claimed_cpus += int(ad["CPUs"])
        ospool_claimed_cpus_count.labels(resource).set(claimed_cpus)

        # idle cpus due to retirement
        idle_retirement_cpus = 0
        ads = collector.query(ad_type=htcondor.AdTypes.Startd,
                              constraint=f"GLIDEIN_ResourceName == \"{resource}\" && PartitionableSlot == true && GLIDEIN_ToRetire < Time() && CPUs >= 1",
                              projection=["CPUs"])
        for ad in ads:
            idle_retirement_cpus += int(ad["CPUs"])
        ospool_idle_retirement_cpus_count.labels(resource).set(idle_retirement_cpus)

        # idle cpus due to memory starvation
        idle_memstarvation_cpus = 0
        ads = collector.query(ad_type=htcondor.AdTypes.Startd,
                              constraint=f"GLIDEIN_ResourceName == \"{resource}\" && PartitionableSlot == true && GLIDEIN_ToRetire > Time() && CPUs >= 1 && Memory < 1000",
                              projection=["CPUs"])
        for ad in ads:
            idle_memstarvation_cpus += int(ad["CPUs"])
        ospool_idle_memstarvation_cpus_count.labels(resource).set(idle_memstarvation_cpus)

        # jobs idle for other reasons
        idle_other_cpus = total_cpus - claimed_cpus - idle_retirement_cpus - idle_memstarvation_cpus
        ospool_idle_other_cpus_count.labels(resource).set(idle_other_cpus)


def cm_submitters_info(collector):
    '''
    Export data on submitters
    '''

    ads = collector.query(ad_type=htcondor.AdTypes.Submitter,
                          projection=["Name", "ScheddName", "IdleJobs", "RunningJobs", "HeldJobs"])
    for ad in ads:
        ospool_submitter_idle_jobs_count.labels(ad["Name"], ad["ScheddName"]).set(int(ad["IdleJobs"]))
        ospool_submitter_running_jobs_count.labels(ad["Name"], ad["ScheddName"]).set(int(ad["RunningJobs"]))
        ospool_submitter_held_jobs_count.labels(ad["Name"], ad["ScheddName"]).set(int(ad["HeldJobs"]))



if __name__ == '__main__':

    try:
        # HTCondor pool
        collector = htcondor.Collector("localhost")

        # test it
        ads = collector.query(ad_type=htcondor.AdTypes.Startd,
                              constraint="True",
                              projection=["Machine"])
    except:
        print("Unable to connect to HTCondor collector. Exiting...")
        time.sleep(20)
        sys.exit(1)

    # Start up the server to expose the metrics.
    start_http_server(8000)

    # collect metrics
    while True:
        # can we determine if we are in ccb or cm mode?
        cm_resources_info(collector)
        cm_submitters_info(collector)
        time.sleep(60)


