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

# metrics
ospool_total_cpus_count = Gauge(f"ospool_total_cpus_count", "Total CPUs", ["resource_name"])
ospool_claimed_cpus_count = Gauge(f"ospool_claimed_cpus_count", "Claimed CPUs", ["resource_name"])
ospool_idle_retirement_cpus_count = Gauge(f"ospool_idle_retirement_cpus_count", "Idle CPUs due to retirement", ["resource_name"])
ospool_idle_starvation_cpus_count = Gauge(f"ospool_idle_starvation_cpus_count", "Idle CPUs due to starvation", ["resource_name"])


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
        total_cpus = 0
        ads = collector.query(ad_type=htcondor.AdTypes.Startd,
                              constraint=f"GLIDEIN_ResourceName == \"{resource}\" && State != \"Unclaimed\"",
                              projection=["CPUs"])
        for ad in ads:
            total_cpus += int(ad["CPUs"])
        ospool_claimed_cpus_count.labels(resource).set(total_cpus)

        # idle cpus due to retirement
        total_cpus = 0
        ads = collector.query(ad_type=htcondor.AdTypes.Startd,
                              constraint=f"GLIDEIN_ResourceName == \"{resource}\" && PartitionableSlot == true && GLIDEIN_ToRetire > Time() && CPUs >= 1",
                              projection=["CPUs"])
        for ad in ads:
            total_cpus += int(ad["CPUs"])
        ospool_idle_retirement_cpus_count.labels(resource).set(total_cpus)

        # idle cpus due to starvation
        total_cpus = 0
        ads = collector.query(ad_type=htcondor.AdTypes.Startd,
                              constraint=f"GLIDEIN_ResourceName == \"{resource}\" && PartitionableSlot == true && GLIDEIN_ToRetire < Time() && CPUs >= 1",
                              projection=["CPUs"])
        for ad in ads:
            total_cpus += int(ad["CPUs"])
        ospool_idle_starvation_cpus_count.labels(resource).set(total_cpus)


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
        time.sleep(60)



