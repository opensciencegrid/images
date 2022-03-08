#!/usr/bin/python
import logging
import time

import classad
import htcondor

logger = logging.getLogger(__name__)

def query_prio_from_neg(coll, negotiator_constraint):
    ads = coll.query(htcondor.AdTypes.Negotiator, negotiator_constraint)
    if len(ads) == 0:
        raise Exception('no negotiator classads found')
    elif len(ads) > 1:
        logger.warning('multiple negotiators found, using %s'%(ads[0]['Name']))
    n = htcondor.Negotiator(ads[0])
    return n.getPriorities()

def get_pool_priorities(pool, retry_delay=30, max_retries=4, last_data={}, negotiator_constraint=True, prefer_accounting=False):
    coll =  htcondor.Collector(pool)
    if callable(negotiator_constraint):
        negotiator_constraint = negotiator_constraint(coll)
    prio = None
    retries = 0
    while retries < max_retries:
        if prefer_accounting:
            prio = coll.query(constraint='MyType=="Accounting"')
            if len(prio) > 0:
                break
            else:
                logger.info("No Accounting ads found in collector {0}, trying negotiator".format(pool))
                try:
                    prio = query_prio_from_neg(coll, negotiator_constraint)
                except Exception as e:
                    logger.info("Error querying negotiator: {0}".format(e))
                else:
                    break
        else:
            try:
                prio = query_prio_from_neg(coll, negotiator_constraint)
            except Exception as e:
                logger.info("Trouble communicating with pool {0} negotiator, trying to get Accounting ads from collector: {1}".format(pool,e))
                prio = coll.query(constraint='MyType=="Accounting"')
                if len(prio) > 0:
                    break
                else:
                    logger.info("No Accounting ads found in collector {0}".format(pool))
            else:
                break
        logger.warning("Unable to collect pool {0} priorities, retrying in {1}s.".format(pool,retry_delay))
        retries += 1
        prio = None
        time.sleep(retry_delay)

    if prio is None:
        logger.error("Unable to collect pool {0} priorities, giving up.".format(pool))
        return {}

    data = last_data
    for p in prio:
        parts = p['Name'].split('@')
        name = parts[0]
        if name.startswith('group_'):
            name = name[6:]
        if len(parts) > 1:
            domain = "".join(parts[1:])
        else:
            domain="unknown"
        if 'NegotiatorName' in p:
            domain=p['NegotiatorName']
        if p.get('IsAccountingGroup',False) and p.get('ConfigQuota',0) > 0:
            basename = "quotas.{0}.{1}".format(
                    domain.replace(".","_").replace("@","_"),
                    name)
            for metric in ["EffectiveQuota",
                        "ConfigQuota",
                        "SubtreeQuota",
                        "Requested"]:
                if metric in p:
                    data[basename+"."+metric] = p[metric]
        else:
            user=name.split('.')[-1]
            group="_".join(name.split('.')[:-1])
            if group == '':
                group = 'none'
            basename = "priorities.{0}.{1}.{2}".format(
                    domain.replace(".","_").replace("@","_"),
                    group,
                    user)
            for metric in ["ResourcesUsed",
                        "AccumulatedUsage",
                        "WeightedAccumulatedUsage",
                        "Priority",
                        "WeightedResourcesUsed",
                        "PriorityFactor"]:
                if metric in p:
                    data[basename+"."+metric] = p[metric]
    return data
