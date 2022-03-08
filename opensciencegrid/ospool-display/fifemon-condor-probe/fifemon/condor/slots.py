#!/usr/bin/python
from collections import defaultdict
import re
import logging
import time
import math

import classad
import htcondor

logger = logging.getLogger(__name__)

def sanitize(key):
    if key is None:
        return None
    return key.replace(".","_").replace("@","-").replace(" ","_")

def slot_weight(cpus, memory, disk):
    """
    Calculate slot weight, where one standard slot is 1 CPU and 2000 MB.
    Weight is returned as float of fractional slots. Examples:
        slot_weight(cpus=1,memory=3000) => 1.5
        slot_weight(cpus=2,memory=3000) => 2.0
    """
    return max(float(cpus),float(memory)/2000)

def unclaimed_slot_weight(cpus, memory, disk):
    """
    Calculate slot weight, where one standard slot is 1 CPU and 2000 MB.
    Weight is returned as min of integral slots. Examples:
        unclaimed_slot_weight(cpus=1,memory=3000) => 1.0
        unclaimed_slot_weight(cpus=2,memory=3000) => 1.0
    """
    return math.floor(min(float(cpus),float(memory)/2000))

def get_pool_resource_utilization(pool, retry_delay=30, max_retries=4, schedd_constraint=True):
    coll =  htcondor.Collector(pool)
    retries = 0
    while retries < max_retries:
        try:
            schedd_ads = coll.query(htcondor.AdTypes.Schedd,schedd_constraint)
        except:
            logger.warning("trouble getting pool {0} schedds, retrying in {1}s.".format(pool,retry_delay))
            retries += 1
            schedd_ads = None
            time.sleep(retry_delay)
        else:
            break

    if schedd_ads is None:
        logger.error("trouble getting pool {0} schedds, giving up.".format(pool))
        return {}

    memory_usage = 0
    disk_usage = 0
    for ad in schedd_ads:
        try:
            schedd = htcondor.Schedd(ad)
            results = schedd.query('jobstatus==2',['ResidentSetSize_RAW','DiskUsage_RAW'])
        except Exception as e:
            logger.error(e)
        else:
            for r in results:
                memory_usage += r.get('ResidentSetSize_RAW',0)
                disk_usage += r.get('DiskUsage_RAW',0)
    return {
        "MemoryUsage":memory_usage/1024,
        "DiskUsage":disk_usage,
    }


def get_pool_slots(pool, retry_delay=30, max_retries=4, totals_only=False, job_resources=True, constraint=True, schedd_constraint=True):
    coll =  htcondor.Collector(pool)
    if callable(constraint):
        constraint=constraint(coll)
    if callable(schedd_constraint):
        schedd_constraint = schedd_constraint(coll)

    retries = 0
    while retries < max_retries:
        try:
            #startd_ads = coll.locateAll(htcondor.DaemonTypes.Startd)
            startd_ads = coll.query(htcondor.AdTypes.Startd, constraint,
                    ['SlotType','State','Name','SlotWeight',
                        'Cpus','TotalSlotCpus','TotalCpus',
                        'Gpus','TotalSlotGpus','TotalGpus',
                        'Disk','TotalSlotDisk','TotalDisk',
                        'Memory','TotalSlotMemory','TotalMemory',
                        'LoadAvg','TotalCondorLoadAvg','TotalLoadAvg',
                        'AccountingGroup','RemoteGroup','RemoteOwner',
                        'kflops','IS_GLIDEIN'])
        except:
            logger.warning("trouble getting pool {0} startds, retrying in {1}s.".format(pool,retry_delay))
            retries += 1
            startd_ads = None
            time.sleep(retry_delay)
        else:
            break

    if startd_ads is None:
        logger.error("trouble getting pool {0} startds, giving up.".format(pool))
        return {}

    data = defaultdict(int)
    load = defaultdict(float)
    for a in startd_ads:
        slot_type = a.get("SlotType", "Static")
        if a.get('IS_GLIDEIN',False):
            slot_type += 'Glidein'
        state = a.get("State", "Unknown")
        kflops = int(a.get("kflops", 0))

        if slot_type in ["Partitionable","PartitionableGlidein"]:
            for k in ["TotalDisk", "TotalSlotDisk", "Disk",
                      "TotalMemory", "TotalSlotMemory", "Memory",
                      "TotalCpus", "TotalSlotCpus", "Cpus",
                      "TotalGpus", "TotalSlotGpus", "Gpus",
                      "TotalLoadAvg", "LoadAvg", "TotalCondorLoadAvg"]:
                metric = ".".join([slot_type, "totals", k])
                data[metric] += a.get(k,0)
                metric = ".".join([slot_type, state, k])
                data[metric] += a.get(k,0)
            metric = ".".join([slot_type, "totals", "NumSlots"])
            data[metric] += 1
            metric = ".".join([slot_type, "totals", "Mflops"])
            data[metric] += long(int(a.get("Cpus",1)) * kflops / 1024)
            metric = ".".join([slot_type, "totals", "StdSlots"])
            data[metric] += unclaimed_slot_weight(a.get("Cpus",1),a.get("Memory",0),a.get("Disk",0))
            if a.get("Cpus",0) == 0 or a.get("Gpus",0) == 0 or a.get("Memory",0) < 2000 or a.get("Disk",0) < 1048576:
                # slot is effectively fully utilized
                for k in ["Disk", "Memory", "Cpus", "Gpus"]:
                    metric = ".".join([slot_type, "unusable", k])
                    data[metric] += a.get(k,0)
        elif state == "Claimed":
            (group,owner) = ("Unknown","Unknown")
            if "AccountingGroup" in a:
                try:
                    m = re.match(r'group_(\S+)\.(\S+)@\S+$',a.eval("AccountingGroup"))
                except:
                    pass
                else:
                    if m:
                        group,owner = m.groups()
            if group == "Unknown" and "RemoteGroup" in a:
                group = a["RemoteGroup"]
                if group == "<none>":
                    group = "None"
            if owner == "Unknown" and "RemoteOwner" in a:
                owner = a["RemoteOwner"].split("@")[0]

            for k in ["Disk", "Memory", "Cpus", "Gpus", "LoadAvg"]:
                if not totals_only:
                    metric = ".".join([slot_type, state, sanitize(group), sanitize(owner), k])
                    data[metric] += a.get(k,0)
                metric = ".".join([slot_type, "totals", k])
                data[metric] += a.get(k,0)
            metric = ".".join([slot_type, "totals", "Mflops"])
            data[metric] += long(int(a.get("Cpus",1)) * kflops / 1024)
            metric = ".".join([slot_type, state, sanitize(group), sanitize(owner), "Weighted"])
            data[metric] += a.eval("SlotWeight")
            metric = ".".join([slot_type, state, sanitize(group), sanitize(owner), "NumSlots"])
            data[metric] += 1
            metric = ".".join([slot_type, state, sanitize(group), sanitize(owner), "StdSlots"])
            data[metric] += slot_weight(a.get("Cpus",1),a.get("Memory",0),a.get("Disk",0))
        else:
            for k in ["Disk", "Memory", "Cpus", "Gpus"]:
                metric = ".".join([slot_type, state, k])
                data[metric] += a.get(k,0)
                metric = ".".join([slot_type, "totals", k])
                data[metric] += a.get(k,0)
            metric = ".".join([slot_type, "totals", "Mflops"])
            data[metric] += int(int(a.get("Cpus",1)) * kflops / 1024)
            metric = ".".join([slot_type, state, "NumSlots"])
            data[metric] += 1
    if job_resources:
        for k,v in get_pool_resource_utilization(pool, retry_delay, max_retries, schedd_constraint).iteritems():
            metric = ".".join(["jobs", "totals", k])
            data[metric] =  v

    return data

def get_pool_glidein_slots(pool, retry_delay=30, max_retries=4):
    coll =  htcondor.Collector(pool)
    retries = 0
    while retries < max_retries:
        try:
            startd_ads = coll.query(htcondor.AdTypes.Startd, 'is_glidein==True',
                    ['GLIDEIN_Site','GLIDEIN_Resource_Name','GLIDEIN_ResourceName','GLIDEIN_Entry_Name','State',
                        'DaemonStartTime','Disk','Memory','Cpus','Gpus'])
        except:
            logger.warning("trouble getting pool {0} startds, retrying in {1}s.".format(pool,retry_delay))
            retries += 1
            startd_ads = None
            time.sleep(retry_delay)
        else:
            break

    if startd_ads is None:
        logger.error("trouble getting pool {0} startds, giving up.".format(pool))
        return {}

    data = defaultdict(int)
    load = defaultdict(float)
    for a in startd_ads:
        site = sanitize(a.get("GLIDEIN_Site", "Unknown"))
        resource = sanitize(a.get("GLIDEIN_Resource_Name",a.get("GLIDEIN_ResourceName","Unknown")))
        entry = sanitize(a.get("GLIDEIN_Entry_Name", "Unknown"))
        state = sanitize(a.get("State", "Unknown"))
        if (time.time() - a.get("DaemonStartTime",time.time())) < 300:
            state = "New"

        metrics = [".".join(["glideins", "totals", "NumSlots"]),
                   ".".join(["glideins", state, "totals", "NumSlots"]),
                   ".".join(["glideins", state, "sites", site, "totals", "NumSlots"]),
                   ".".join(["glideins", state, "sites", site, "resources", resource, "NumSlots"]),
                   ".".join(["glideins", state, "sites", site, "entries", entry, "NumSlots"])]
        for m in metrics:
            data[m] += 1

        metrics = [".".join(["glideins", "totals", "StdSlots"]),
                   ".".join(["glideins", state, "totals", "StdSlots"]),
                   ".".join(["glideins", state, "sites", site, "totals", "StdSlots"]),
                   ".".join(["glideins", state, "sites", site, "resources", resource, "StdSlots"]),
                   ".".join(["glideins", state, "sites", site, "entries", entry, "StdSlots"])]
        for m in metrics:
            if state=="Unclaimed":
                data[m] += unclaimed_slot_weight(a.get("Cpus",1),a.get("Memory",0),a.get("Disk",0))
            else:
                data[m] += slot_weight(a.get("Cpus",1),a.get("Memory",0),a.get("Disk",0))

        for k in ["Disk", "Memory", "Cpus", "Gpus"]:
            metrics = [".".join(["glideins", "totals", k]),
                       ".".join(["glideins", state, "totals", k]),
                       ".".join(["glideins", state, "sites", site, "totals", k]),
                       ".".join(["glideins", state, "sites", site, "resources", resource, k]),
                       ".".join(["glideins", state, "sites", site, "entries", entry, k])]
            for m in metrics:
                data[m] += a.get(k,0)

    return data

if __name__ == "__main__":
    import pprint
    pprint.pprint(dict(get_pool_slots("cmssrv221")))
