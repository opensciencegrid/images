#!/usr/bin/python3

'''
Prometheus monitor for the OSPool
'''

import htcondor2
import classad2
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
ospool_idle_blackhole_cpus_count = Gauge("ospool_idle_blackhole_cpus_count", "Idle CPUs due to black hole trigger", ["resource_name"])
ospool_idle_other_cpus_count = Gauge("ospool_idle_other_cpus_count", "Idle CPUs due to other reasons", ["resource_name"])

# gpus
ospool_total_gpus_count = Gauge("ospool_total_gpus_count", "Total GPUs", ["resource_name"])
ospool_claimed_gpus_count = Gauge("ospool_claimed_gpus_count", "Claimed GPUs", ["resource_name"])
ospool_idle_gpus_count = Gauge("ospool_idle_gpus_count", "Idle GPUs", ["resource_name"])

# pool wide attributes
ospool_machine_ads = Gauge("ospool_machine_ads", "HTCondor machine ads")
ospool_kernel_version = Gauge("ospool_kernel_versions", "Kernel versions in the pool", ["kernel_version"])
ospool_glidein_version = Gauge("ospool_glidein_version", "Versions in the pool", ["glidein_version"])
ospool_glidein_group = Gauge("ospool_glidein_group", "GWMS client group", ["glidein_group"])
ospool_microarch = Gauge("ospool_microarch", "CPU Microarch", ["microarch"])
ospool_default_os = Gauge("ospool_default_os", "Default OS", ["default_os"])
ospool_cvmfs = Gauge("ospool_cvmfs", "CVMFS availabilty in the pool")
ospool_osdf = Gauge("ospool_osdf", "Resources with a working OSDF")
ospool_apptainer = Gauge("ospool_apptainer", "Resources with a working Apptainer/Singularity")
ospool_apptainer_sif = Gauge("ospool_apptainer_sif", "Resources with Apptainer/Singularity SIF capability")
ospool_firewall =  Gauge("ospool_firewall", "Resources with a firewall blocking some of our standard ports")

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
        "idle_blackhole_cpus": 0,
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
    ads = collector.query(ad_type=htcondor2.AdTypes.Startd,
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
    ads = collector.query(ad_type=htcondor2.AdTypes.Startd,
                          constraint="!isUndefined(GLIDEIN_ResourceName) && PartitionableSlot == true && CPUs >= 1",
                          projection=["GLIDEIN_ResourceName", "CPUs", "Disk", "Memory", "GLIDEIN_ToRetire", "isBlackHole", "RecentJobDurationAvg", "RecentJobDurationCount"])
    now = time.time()
    for ad in ads:
        r = resources[ad["GLIDEIN_ResourceName"]]
        if "GLIDEIN_ToRetire" in ad and int(ad["GLIDEIN_ToRetire"]) < now:
            r["idle_retirement_cpus"] += int(ad["CPUs"])
        elif int(ad["Memory"]) < mem_starvation:
            r["idle_memstarvation_cpus"] += int(ad["CPUs"])
        elif int(ad["Disk"]) < disk_starvation:
            r["idle_diskstarvation_cpus"] += int(ad["CPUs"])
        elif "isBlackHole" in ad and isinstance(ad["isBlackHole"], classad2.ExprTree) and ad["isBlackHole"].eval(scope=ad) == True:
            r["idle_blackhole_cpus"] += int(ad["CPUs"])
        else:
            r["idle_other_cpus"] += int(ad["CPUs"])

    # done collecting data, update Prometheus
    for resource, data in resources.items():
        
        ospool_total_cpus_count.labels(resource).set(data["total_cpus"])
        ospool_claimed_cpus_count.labels(resource).set(data["claimed_cpus"])

        ospool_idle_retirement_cpus_count.labels(resource).set(data["idle_retirement_cpus"])
        ospool_idle_memstarvation_cpus_count.labels(resource).set(data["idle_memstarvation_cpus"])
        ospool_idle_diskstarvation_cpus_count.labels(resource).set(data["idle_diskstarvation_cpus"])
        ospool_idle_blackhole_cpus_count.labels(resource).set(data["idle_blackhole_cpus"])

        # jobs idle for other reasons
        idle_other_cpus = data["total_cpus"] - data["claimed_cpus"] \
                          - data["idle_retirement_cpus"] \
                          - data["idle_memstarvation_cpus"] \
                          - data["idle_diskstarvation_cpus"] \
                          - data["idle_blackhole_cpus"]
        ospool_idle_other_cpus_count.labels(resource).set(idle_other_cpus)

        ospool_total_gpus_count.labels(resource).set(data["total_gpus"])
        ospool_claimed_gpus_count.labels(resource).set(data["claimed_gpus"])
        ospool_idle_gpus_count.labels(resource).set(data["idle_gpus"])


def cm_pool_attributes(collector):
    '''
    Pool wide attributes
    '''

    machine_ads = 0
    kernel_version = defaultdict(int)
    glidein_version = defaultdict(int)
    glidein_group = defaultdict(int)
    microarch = defaultdict(int)
    default_os = defaultdict(int)
    cvmfs = 0
    osdf = 0
    apptainer = 0
    apptainer_sif = 0
    firewall = 0

    # iterate over all resources
    ads = collector.query(ad_type=htcondor2.AdTypes.Startd,
                          constraint="!isUndefined(GLIDEIN_ResourceName)",
                          projection=["OSG_GLIDEIN_VERSION",
                                      "GLIDECLIENT_Group",
                                      "Arch",
                                      "Microarch",
                                      "OSG_OS_STRING",
                                      "HAS_CVMFS_singularity_opensciencegrid_org",
                                      "OSDF_VERIFIED",
                                      "HAS_SINGULARITY",
                                      "SINGULARITY_CAN_USE_SIF",
                                      "PORT_80",
                                      "PORT_1094",
                                      "PORT_2880",
                                      "PORT_8000",
                                      "PORT_8443",
                                      "PORT_27017",
                                      "OSG_OS_KERNEL"])
    for ad in ads:
        machine_ads += 1
        if "OSG_OS_KERNEL" in ad:
            # simplify version
            kversion = re.sub("\.[0-9]+-.*", "", ad["OSG_OS_KERNEL"])
            kernel_version[kversion] += 1
        if "OSG_GLIDEIN_VERSION" in ad:
            glidein_version[ad["OSG_GLIDEIN_VERSION"]] += 1
        if "GLIDECLIENT_Group" in ad:
            glidein_group[ad["GLIDECLIENT_Group"]] += 1
        if "Microarch" in ad:
            microarch[ad["Microarch"]] += 1
        elif "Arch" in ad:
            microarch[ad["Arch"]] += 1
        if "OSG_OS_STRING" in ad:
            default_os[ad["OSG_OS_STRING"]] += 1
        if "HAS_CVMFS_singularity_opensciencegrid_org" in ad and \
           ad.eval("HAS_CVMFS_singularity_opensciencegrid_org"):
            cvmfs += 1
        if "OSDF_VERIFIED" in ad and \
           ad.eval("OSDF_VERIFIED"):
            osdf += 1
        if "HAS_SINGULARITY" in ad and \
           ad.eval("HAS_SINGULARITY"):
            apptainer += 1
        if "SINGULARITY_CAN_USE_SIF" in ad and \
           ad.eval("SINGULARITY_CAN_USE_SIF"):
            apptainer_sif += 1

        # firewall if any of the ports fails
        found_firewall = False
        for port in ["PORT_80",
                     "PORT_1094",
                     "PORT_2880",
                     "PORT_8000",
                     "PORT_8443",
                     "PORT_27017"]:
            if not (port in ad and ad.eval(port)):
                found_firewall = True
        if found_firewall:
            firewall += 1

    # now report
    ospool_machine_ads.set(machine_ads)
    for version, count in kernel_version.items():
        ospool_kernel_version.labels(version).set(count)
    for version, count in glidein_version.items():
        ospool_glidein_version.labels(version).set(count)
    for group, count in glidein_group.items():
        ospool_glidein_group.labels(group).set(count)
    for arch, count in microarch.items():
        ospool_microarch.labels(arch).set(count)
    for o, count in default_os.items():
        ospool_default_os.labels(o).set(count)
    ospool_cvmfs.set(cvmfs)
    ospool_osdf.set(osdf)
    ospool_apptainer.set(apptainer)
    ospool_apptainer_sif.set(apptainer_sif)
    ospool_firewall.set(firewall)


def cm_submitters_info(collector):
    '''
    Export data on submitters
    '''

    ads = collector.query(ad_type=htcondor2.AdTypes.Submitter,
                          projection=["Name", "ScheddName", "IdleJobs", "RunningJobs", "HeldJobs"])
    for ad in ads:
        ospool_submitter_idle_jobs_count.labels(ad["Name"], ad["ScheddName"]).set(int(ad["IdleJobs"]))
        ospool_submitter_running_jobs_count.labels(ad["Name"], ad["ScheddName"]).set(int(ad["RunningJobs"]))
        ospool_submitter_held_jobs_count.labels(ad["Name"], ad["ScheddName"]).set(int(ad["HeldJobs"]))



if __name__ == '__main__':

    try:
        # HTCondor pool
        collector = htcondor2.Collector("127.0.0.1")

        # test it
        ads = collector.query(ad_type=htcondor2.AdTypes.Startd,
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
        cm_pool_attributes(collector)
        cm_submitters_info(collector)
        time.sleep(20)


