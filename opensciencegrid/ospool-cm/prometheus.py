#!/usr/bin/python3

'''
Prometheus monitor for the OSPool
'''

import htcondor
import re
import sys
import time

from collections import defaultdict
from pprint import pprint
from prometheus_client import start_http_server, Gauge, Counter

# resource metrics
ospool_total_cpus_count = Gauge("ospool_total_cpus_count", "Total CPUs", ["resource_name"])
ospool_claimed_cpus_count = Gauge("ospool_claimed_cpus_count", "Claimed CPUs", ["resource_name"])
ospool_idle_retirement_cpus_count = Gauge("ospool_idle_retirement_cpus_count", "Idle CPUs due to retirement", ["resource_name"])
ospool_idle_memstarvation_cpus_count = Gauge("ospool_idle_memstarvation_cpus_count", "Idle CPUs due to memory starvation", ["resource_name"])
ospool_idle_diskstarvation_cpus_count = Gauge("ospool_idle_diskstarvation_cpus_count", "Idle CPUs due to disk starvation", ["resource_name"])
ospool_idle_other_cpus_count = Gauge("ospool_idle_other_cpus_count", "Idle CPUs due to other reasons", ["resource_name"])

# gpus
ospool_total_gpus_count = Gauge("ospool_total_gpus_count", "Total GPUs", ["resource_name"])
ospool_claimed_gpus_count = Gauge("ospool_claimed_gpus_count", "Claimed GPUs", ["resource_name"])
ospool_idle_gpus_count = Gauge("ospool_idle_gpus_count", "Idle GPUs", ["resource_name"])

# submitter metrics
ospool_submitter_idle_jobs_count = Gauge("ospool_submitter_idle_jobs_count", "Submitter idle jobs", ["submitter", "schedd"])
ospool_submitter_running_jobs_count = Gauge("ospool_submitter_running_jobs_count", "Submitter running jobs", ["submitter", "schedd"])
ospool_submitter_held_jobs_count = Gauge("ospool_submitter_held_jobs_count", "Submitter held jobs", ["submitter", "schedd"])


def entry_factory():
    '''
    Make sure we have a base entry for given resource
    '''
    entry = {
        "total_cpus": 0,
        "claimed_cpus": 0,
        "idle_retirement_cpus": 0,
        "idle_memstarvation_cpus": 0,
        "idle_diskstarvation_cpus": 0,
        "idle_other_cpus": 0,
        "total_gpus": 0,
        "claimed_gpus": 0,
        "idle_gpus": 0,
    }
    return entry


def cm_resources_info(collector):
    '''
    Discover the sites, and then query for specifics per site.
    Can we do this in a single query?
    '''
    resources = defaultdict(entry_factory)

    # These are the limits we use to determine if a pslot is being
    # starved. Memory is in MB, Disk in KB.
    mem_starvation = 5000
    disk_starvation = 5000000

    # iterate over all resources
    ads = collector.query(ad_type=htcondor.AdTypes.Startd,
                          constraint="!isUndefined(GLIDEIN_ResourceName)",
                          projection=["GLIDEIN_ResourceName", "CPUs", "GPUs", "State"])
    for ad in ads:
        r = resources[ad["GLIDEIN_ResourceName"]]
        r["total_cpus"] += int(ad["CPUs"])
        if ad["State"] != "Unclaimed":
            r["claimed_cpus"] += int(ad["CPUs"])

        # gpus
        if "GPUs" in ad:
            r["total_gpus"] += int(ad["GPUs"])
            if ad["State"] != "Unclaimed":
                r["claimed_gpus"] += int(ad["GPUs"])
            r["idle_gpus"] = r["total_gpus"] - r["claimed_gpus"]

    # classify idle CPUs
    ads = collector.query(ad_type=htcondor.AdTypes.Startd,
                          constraint="!isUndefined(GLIDEIN_ResourceName) && PartitionableSlot == true && CPUs >= 1",
                          projection=["GLIDEIN_ResourceName", "CPUs", "Disk", "Memory", "GLIDEIN_ToRetire"])
    now = time.time()
    for ad in ads:
        r = resources[ad["GLIDEIN_ResourceName"]]
        if "GLIDEIN_ToRetire" in ad and int(ad["GLIDEIN_ToRetire"]) < now:
            r["idle_retirement_cpus"] += int(ad["CPUs"])
        elif int(ad["Memory"]) < mem_starvation:
            r["idle_memstarvation_cpus"] += int(ad["CPUs"])
        elif int(ad["Disk"]) < disk_starvation:
            r["idle_diskstarvation_cpus"] += int(ad["CPUs"])
        else:
            r["idle_other_cpus"] += int(ad["CPUs"])

    # done collecting data, update Prometheus
    for resource, data in resources.items():
        
        ospool_total_cpus_count.labels(resource).set(data["total_cpus"])
        ospool_claimed_cpus_count.labels(resource).set(data["claimed_cpus"])

        ospool_idle_retirement_cpus_count.labels(resource).set(data["idle_retirement_cpus"])
        ospool_idle_memstarvation_cpus_count.labels(resource).set(data["idle_memstarvation_cpus"])
        ospool_idle_diskstarvation_cpus_count.labels(resource).set(data["idle_diskstarvation_cpus"])

        # jobs idle for other reasons
        idle_other_cpus = data["total_cpus"] - data["claimed_cpus"] \
                          - data["idle_retirement_cpus"] \
                          - data["idle_memstarvation_cpus"] \
                          - data["idle_diskstarvation_cpus"]
        ospool_idle_other_cpus_count.labels(resource).set(idle_other_cpus)

        ospool_total_gpus_count.labels(resource).set(data["total_gpus"])
        ospool_claimed_gpus_count.labels(resource).set(data["claimed_gpus"])
        ospool_idle_gpus_count.labels(resource).set(data["idle_gpus"])


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
        collector = htcondor.Collector("127.0.0.1")

        # test it
        ads = collector.query(ad_type=htcondor.AdTypes.Startd,
                              constraint="True",
                              projection=["Machine"])
    except Exception as err:
        print("Unable to connect to HTCondor collector due to %s" % err)
        print("Exiting...")
        time.sleep(20)
        sys.exit(1)

    # Start up the server to expose the metrics.
    start_http_server(8000)

    # collect metrics
    while True:
        # can we determine if we are in ccb or cm mode?
        cm_resources_info(collector)
        cm_submitters_info(collector)
        time.sleep(20)


