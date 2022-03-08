#!/usr/bin/python
import logging
import time

import classad
import htcondor

logger = logging.getLogger(__name__)


def get_pool_status(pool, retry_delay=30, max_retries=4, schedd_constraint=True, negotiator_constraint=True):
    coll =  htcondor.Collector(pool)
    if callable(schedd_constraint):
        schedd_constraint = schedd_constraint(coll)
    if callable(negotiator_constraint):
        negotiator_constraint = negotiator_constraint(coll)

    daemons = {"schedds": htcondor.DaemonTypes.Schedd,
               "collectors": htcondor.DaemonTypes.Collector,
               "negotiators": htcondor.DaemonTypes.Negotiator}

    data = {
            "schema": "daemon.name.measurement",
            "metrics": {},
            }
    for daemon_type, daemon in daemons.iteritems():
        retries = 0
        while retries < max_retries:
            try:
                if daemon_type == "schedds":
                    ads = coll.query(htcondor.AdTypes.Schedd,schedd_constraint)
                elif daemon_type == 'negotiators':
                    ads = coll.query(htcondor.AdTypes.Negotiator, negotiator_constraint)
                else:
                    ads = coll.locateAll(daemon)
            except Exception as e:
                logger.warning("trouble getting pool {0} {1} status, retrying in {2}s: {3}".format(pool,daemon_type,retry_delay,e))
                ads = None
                retries += 1
                time.sleep(retry_delay)
            else:
                break
        if ads is None:
            logger.error("trouble getting pool {0} {1} status, giving up.".format(pool,daemon_type))
        else:
            for ad in ads:
                # quick hack to skip schedds starting up on worker nodes
                if ad['Name'].startswith('fnpc'):
                    logger.info('skipping worker node {}'.format(ad['Name']))
                    continue
                for k in ad:
                    if type(ad[k]) in [int,long,float]:
                        metric = ".".join([daemon_type, ad["Name"].replace(".","_").replace("@","-").replace(" ","_"), k])
                        data["metrics"][metric] = ad[k]
    return [data]
