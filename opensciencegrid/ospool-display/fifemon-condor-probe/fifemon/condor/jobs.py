#!/usr/bin/python
import time
from collections import defaultdict, deque
import logging
from threading import Thread
import traceback
import re
import urllib

import classad
import htcondor

logger = logging.getLogger(__name__)


def find_bin(value, bins):
    for b in bins:
        if value < b[0]:
            return b[1]
    return "longer"


def clean_metric_name(s):
    """
    replaces any non-standard characters with _
    """
    if s is None:
        return "None"
    if len(s) == 0:
        return "None"
    # still have a string, url encode it
    #return re.sub(r'[^a-zA-Z0-9_\-.]', '_', s)
    return urllib.quote_plus(s)


def geteval(self, key, default=None):
    """
    get an attribute from the classad, returning default if not found.
    if the attribute is an expression, eval() it.
    """
    r = self.get(key,default)
    if isinstance(r, classad.ExprTree):
        e = r.eval()
        if isinstance(e, classad.Value):
            # Undefined / Error
            return default
        return e
    return r

classad.ClassAd.geteval = geteval


def job_metrics(job_classad):
    """
    Returns a list of base metrics for the given job.
    """
    counters = []

    try:
        user_name = job_classad.get("Owner","unknown")
    except:
        user_name = "unknown"
    try:
        groups = re.findall(r'(?:group_)?(\w+)',job_classad.get("AccountingGroup","group_unknown"))
        exp_name = groups[0]
        subgroups = []
        if len(groups) > 1:
            # sometimes each user has an accounting group, we don't want those
            if groups[-1] == user_name:
                subgroups = groups[1:len(groups)-1]
            else:
                subgroups = groups[1:]
    except:
        exp_name = "unknown"
        subgroups = []

    project = job_classad.geteval("ProjectName","Unknown")
    try:
        project = re.sub(r'^.*\.', '', project)
    except:
        pass
    project = clean_metric_name(project)

    simg = job_classad.geteval("SingularityImage","None")
    try:
        simg = re.sub(r'^/cvmfs/[^/]+/', '', simg)
        simg = re.sub(r'\.', '_', simg)
        simg = re.sub(r'/', '__', simg)
        simg = re.sub(r':', '__', simg)
    except:
        pass
    simg = clean_metric_name(simg)

    if job_classad["JobUniverse"] == 7:
        counters = [".dag.totals"]
    elif job_classad["JobStatus"] == 1:
        counters = [".idle.totals"]
        if "DESIRED_usage_model" in job_classad:
            models = set(job_classad["DESIRED_usage_model"].split(","))
            if "DESIRED_Sites" in job_classad:
                sites = job_classad["DESIRED_Sites"].split(",")
                for s in sites:
                    counters.append(".idle.sites."+s)
                #if "Fermigrid" not in sites:
                #    models.discard("DEDICATED")
                #    models.discard("OPPORTUNISTIC")
            models_sorted = list(models)
            if len(models_sorted) == 0:
                models_sorted = ["impossible"]
            else:
                models_sorted.sort()
            counters.append(".idle.usage_models." + "_".join(models_sorted))
        else:
            counters.append(".idle.usage_models.unknown")
    elif job_classad["JobStatus"] == 2:
        counters = [".running.totals"]
        if "MATCH_EXP_JOBGLIDEIN_ResourceName" in job_classad:
            site = job_classad["MATCH_EXP_JOBGLIDEIN_ResourceName"]
            counters.append(".running.sites." + site)
        else:
            counters.append(".running.sites.unknown")
    elif job_classad["JobStatus"] == 5:
        counters = [".held.totals"]
    else:
        counters = [".unknown.totals"]

    metrics = []
    for counter in counters:
        metrics.append("totals"+counter)
        metrics.append("experiments."+exp_name+".totals"+counter)
        metrics.append("experiments."+exp_name+".users."+user_name+counter)
        if len(subgroups) > 0:
            metrics.append("experiments."+exp_name+".subgroups."+".".join(subgroups)+'.'+counter)
        metrics.append("projects."+project+".totals"+counter)
        metrics.append("projects."+project+".users."+user_name+counter)
        metrics.append("requested_singularity."+simg+".totals"+counter)
        metrics.append("requested_singularity."+simg+".users."+user_name+counter)
        metrics.append("users."+user_name+counter)
    return metrics


def get_jobs(job_q, schedd_ad, constraint=True, attrs=['ClusterId','ProcId','JobStatus'], retry_delay=30, max_retries=4):
    retries=0
    while retries < max_retries:
        try:
            schedd = htcondor.Schedd(schedd_ad)
            results = schedd.query(constraint, attrs)
        except IOError:
            traceback.print_exc()
            retries += 1
            if retries < max_retries:
                logger.warning("Trouble communicating with schedd {0}, retrying in {1}s.".format(schedd_ad['Name'],retry_delay))
                time.sleep(retry_delay)
            else:
                logger.warning("Trouble communicating with schedd {0}, giving up.".format(schedd_ad['Name']))
            continue
        else:
            for r in results:
                job_q.append(r)
            return
    logger.error("Trouble communicating with schedd {0}, giving up.".format(schedd_ad['Name']))

def get_idle_jobs(job_q, schedd_ad, retry_delay=30, max_retries=4):
    get_jobs(job_q, schedd_ad, constraint='JobStatus==1', retry_delay=retry_delay, max_retries=max_retries,
            attrs=["ClusterId","ProcId","Owner",
                "NumJobStarts", "NumShadowStarts", "NumHolds", "NumSystemHolds",
                "AccountingGroup","ProjectName","JobStatus",
                "SingularityImage",
                "DESIRED_usage_model","DESIRED_Sites","JobUniverse",
                "QDate","ServerTime",
                "RequestMemory","RequestDisk","RequestCpus","RequestGpus"])

def get_running_jobs(job_q, schedd_ad, retry_delay=30, max_retries=4):
    get_jobs(job_q, schedd_ad, constraint='JobStatus==2', retry_delay=retry_delay, max_retries=max_retries,
            attrs=["ClusterId","ProcId","Owner",
                "NumJobStarts", "NumShadowStarts", "NumHolds", "NumSystemHolds",
                "MATCH_GLIDEIN_Site","MATCH_EXP_JOBGLIDEIN_ResourceName",
                "AccountingGroup","ProjectName","JobStatus",
                "SingularityImage",
                "JobUniverse",
                "ServerTime","JobCurrentStartDate","RemoteUserCpu",
                "RequestMemory","ResidentSetSize_RAW",
                "RequestDisk","DiskUsage_RAW","RequestCpus","RequestGpus"])

def get_held_jobs(job_q, schedd_ad, retry_delay=30, max_retries=4):
    get_jobs(job_q, schedd_ad, constraint='JobStatus==5', retry_delay=retry_delay, max_retries=max_retries,
            attrs=["ClusterId","ProcId","Owner",
                "NumJobStarts", "NumShadowStarts", "NumHolds", "NumSystemHolds",
                "AccountingGroup","ProjectName","JobStatus",
                "SingularityImage",
                "JobUniverse",
                "ServerTime",
                "EnteredCurrentStatus"])


class Jobs(object):
    def __init__(self, pool="localhost"):
        self.pool = pool
        self.collector = htcondor.Collector(pool)
        self.bins=[(300,       'recent'),
                   (3600,      'one_hour'),
                   (3600*4,    'four_hours'),
                   (3600*8,    'eight_hours'),
                   (3600*24,   'one_day'),
                   (3600*24*2, 'two_days'),
                   (3600*24*7, 'one_week')]


    def job_walltime(self, job_classad):
        now = job_classad.get("ServerTime",0)
        start = job_classad.get("JobCurrentStartDate",now)
        return (now-start)*job_classad.geteval("RequestCpus",1)

    def job_cputime(self, job_classad):
        return job_classad.get("RemoteUserCpu",0)

    def job_bin(self, job_classad):
        bin = None
        if job_classad["JobStatus"] == 1:
            if "ServerTime" in job_classad and "QDate" in job_classad:
                qage = job_classad["ServerTime"]-job_classad["QDate"]
                bin = ".count_"+find_bin(qage, self.bins)
            else:
                bin = ".count_unknown"
        elif job_classad["JobStatus"] == 2:
            walltime = self.job_walltime(job_classad)
            if walltime > 0:
                bin = ".count_"+find_bin(walltime, self.bins)
            else:
                bin = ".count_unknown"
        elif job_classad["JobStatus"] == 5:
            if "ServerTime" in job_classad and "EnteredCurrentStatus" in job_classad:
                holdage = job_classad["ServerTime"]-job_classad["EnteredCurrentStatus"]
                bin = ".count_holdage_"+find_bin(holdage, self.bins)
            else:
                bin = ".count_holdage_unknown"
        return bin


    def get_job_count(self, retry_delay=30, max_retries=4, schedd_constraint=True):
        if callable(schedd_constraint):
            schedd_constraint=schedd_constraint(self.collector)
        try:
            ads = self.collector.query(htcondor.AdTypes.Schedd,schedd_constraint)
        except:
            logger.error("Trouble getting pool {0} schedds.".format(self.pool))
            return None

        job_q = deque()
        ## spawn off workers to query each schedd and put metrics for each job in a queue
        for a in ads:
            get_idle_jobs(job_q,a,retry_delay,max_retries)
            get_running_jobs(job_q,a,retry_delay,max_retries)
            get_held_jobs(job_q,a,retry_delay,max_retries)

        logger.info("Processing jobs")
        counts = defaultdict(int)
        for r in job_q:
            for m in job_metrics(r):
                counts[m+".count"] += 1

                bin = self.job_bin(r)
                if bin is not None:
                    counts[m+bin] += 1

                walltime = self.job_walltime(r)
                cputime = self.job_cputime(r)
                if walltime > 0 and cputime > 0:
                    try:
                        counts[m+".walltime"] += walltime
                        counts[m+".cputime"] += cputime
                        counts[m+".efficiency"] = max(min(counts[m+".cputime"]/counts[m+".walltime"]*100,100),0)
                        counts[m+".wastetime"] = counts[m+".walltime"]-counts[m+".cputime"]
                        if walltime > counts[m+".walltime_max"]:
                            counts[m+".walltime_max"] = walltime
                        if counts[m+".count"] > 0:
                            counts[m+".walltime_avg"] = counts[m+".walltime"]/counts[m+".count"]
                            counts[m+".wastetime_avg"] = counts[m+".wastetime"]/counts[m+".count"]
                    except:
                        logger.warning("Problem with walltime: {0} {1} {2}".format(walltime, counts[m+".walltime"], counts[m+".count"]))

                if "NumJobStarts" in r:
                    starts = r.eval("NumJobStarts")
                    try:
                        counts[m+".job_starts"] += starts
                    except:
                        pass
                if "NumShadowStarts" in r:
                    starts = r.eval("NumShadowStarts")
                    try:
                        counts[m+".shadow_starts"] += starts
                    except:
                        pass
                if "NumHolds" in r:
                    holds = r.eval("NumHolds")
                    try:
                        counts[m+".holds"] += holds
                    except:
                        pass
                if "NumSystemHolds" in r:
                    holds = r.eval("NumSystemHolds")
                    try:
                        counts[m+".holds_system"] += holds
                    except:
                        pass

                ## one standard slot == 1 cpu and 2000 MB of memory (undefined amount of disk)
                std_slots = 1
                if "RequestCpus" in r:
                    cpus = r.eval("RequestCpus")
                    try:
                        counts[m+".cpu_request"] += cpus
                        std_slots = max(std_slots,cpus)
                    except:
                        pass
                if "RequestGpus" in r:
                    gpus = r.eval("RequestGpus")
                    try:
                        if int(gpus) == gpus:
                            counts[m+".gpu_request"] += gpus
                            std_slots = max(std_slots,gpus)
                    except:
                        pass
                if "RequestMemory" in r:
                    mem = r.eval("RequestMemory")
                    try:
                        counts[m+".memory_request_b"] += mem*1024.0*1024.0
                        std_slots = max(std_slots,mem/2000.0)
                    except:
                        pass
                if "RequestDisk" in r:
                    try:
                        counts[m+".disk_request_b"] += r.eval("RequestDisk")*1024
                    except:
                        pass
                counts[m+".std_slots"] += std_slots

                if r["JobStatus"] == 2:
                    if "ResidentSetSize_RAW" in r:
                        counts[m+".memory_usage_b"] += r.eval("ResidentSetSize_RAW")*1024
                    if "DiskUsage_RAW" in r:
                        counts[m+".disk_usage_b"] += r.eval("DiskUsage_RAW")*1024

        return counts
