#!/usr/bin/python
from collections import defaultdict
import re
from optparse import OptionParser
import logging
import time
import os
import ConfigParser
import pprint

from fifemon import Probe, condor

logger = logging.getLogger(__name__)

class CondorProbe(Probe):
    """
    Query HTCondor pool and post statistics to Graphite.

    Options:
        post_pool_status:   collect main daemon (schedd, collector,
                            negotiator) statistics
        post_pool_slots:    collect & aggregate slot (startd) status
        slot_constraint:    optional constraint to filter slots (bool, str, or func)
        post_pool_glideins: collect & aggregate glidein slot status
        post_pool_prio:     collect user priorities
        negotiator_constraint: optional constraint to filter negotiators queried (bool, str, or func)
        prefer_accounting:  prefer accounting classads from collector over directly querying negotiator
                            (in either case the other will be tried if there's a problem with the first)
        post_pool_jobs:     collect & aggregate user job status
        schedd_constraint:  optional constraint to filter schedds queried (bool, str, or func)
    """

    def __init__(self, *args, **kwargs):
        self.pool = kwargs.pop('pool', 'localhost')
        self.post_pool_status = kwargs.pop('post_pool_status',True)
        self.post_pool_slots = kwargs.pop('post_pool_slots',True)
        self.slot_constraint = kwargs.pop('slot_constraint',True)
        self.post_pool_glideins = kwargs.pop('post_pool_glideins',False)
        self.post_pool_prio = kwargs.pop('post_pool_prio',True)
        self.negotiator_constraint = kwargs.pop('negotiator_constraint',True)
        self.prefer_accounting = kwargs.pop('prefer_accounting', False)
        self.post_pool_jobs = kwargs.pop('post_pool_jobs',False)
        self.schedd_constraint = kwargs.pop('schedd_constraint',True)
        self.use_gsi_auth = kwargs.pop('use_gsi_auth',False)
        self.x509_user_key = kwargs.pop('x509_user_key',"")
        self.x509_user_cert = kwargs.pop('x509_user_cert',"")

        if self.post_pool_jobs:
            self.jobs = condor.Jobs(self.pool)

        self.last_prio={}

        super(CondorProbe, self).__init__(*args, **kwargs)

    def post(self):
        if self.use_gsi_auth:
            save_key = os.environ.get('X509_USER_KEY')
            os.environ['X509_USER_KEY'] = self.x509_user_key
            save_cert = os.environ.get('X509_USER_CERT')
            os.environ['X509_USER_CERT'] = self.x509_user_cert

        if self.post_pool_status:
            logger.info('querying pool {0} status'.format(self.pool))
            data = condor.get_pool_status(self.pool, self.delay, self.retries,
                                          schedd_constraint=self.schedd_constraint,
                                          negotiator_constraint=self.negotiator_constraint)
            for dataset in data:
                if self.use_graphite:
                    self.graphite.send_dict(self.namespace,
                            dataset["metrics"],
                            send_data=(not self.test))
                if self.use_influxdb:
                    self.influxdb.send_dict(dataset["metrics"],
                            send_data=(not self.test),
                            schema=dataset["schema"],
                            tags=self.influxdb_tags)
        if self.post_pool_slots not in [False, 'false', 'False']:
            if self.post_pool_slots == "totals":
                logger.info('querying pool {0} slots (totals only)'.format(self.pool))
                data = condor.get_pool_slots(self.pool, self.delay, self.retries,
                                             totals_only=True, job_resources=False,
                                             constraint=self.slot_constraint,
                                             schedd_constraint=self.schedd_constraint)
            else:
                logger.info('querying pool {0} slots'.format(self.pool))
                data = condor.get_pool_slots(self.pool, self.delay, self.retries,
                                             constraint=self.slot_constraint,
                                             schedd_constraint=self.schedd_constraint)
            if self.use_graphite:
                self.graphite.send_dict(self.namespace+".slots", data, send_data=(not self.test))
        if self.post_pool_glideins:
            logger.info('querying pool {0} glidein slots'.format(self.pool))
            data = condor.get_pool_glidein_slots(self.pool, self.delay, self.retries)
            if self.use_graphite:
                self.graphite.send_dict(self.namespace+".slots", data, send_data=(not self.test))
        if self.post_pool_prio:
            logger.info('querying pool {0} priorities'.format(self.pool))
            data = condor.get_pool_priorities(self.pool, self.delay, self.retries, self.last_prio,
                                              negotiator_constraint=self.negotiator_constraint,
                                              prefer_accounting=self.prefer_accounting)
            self.last_prio = data
            if self.use_graphite:
                self.graphite.send_dict(self.namespace, data, send_data=(not self.test))
        if self.post_pool_jobs:
            logger.info('querying pool {0} jobs'.format(self.pool))
            data = self.jobs.get_job_count(self.delay, self.retries,
                                           schedd_constraint=self.schedd_constraint)
            if self.use_graphite:
                self.graphite.send_dict(self.namespace+".jobs", data, send_data=(not self.test))

        if self.use_gsi_auth:
            if save_key is None:
                del os.environ['X509_USER_KEY']
            else:
                os.environ['X509_USER_KEY'] = save_key
            if save_cert is None:
                del os.environ['X509_USER_CERT']
            else:
                os.environ['X509_USER_CERT'] = save_cert

def get_options():
    parser = OptionParser(usage="usage: %prog [options] [config file(s)]")
    parser.add_option('-t','--test',action="store_true",
            help="output data to stdout, don't send to graphite (implies --once)")
    parser.add_option('-1','--once',action="store_true",
            help="run once and exit")
    parser.add_option('-p','--port',type='int',default=8100,
            help="port on which to publish HTTP metrics")
    (cmd_opts,args) = parser.parse_args()

    config = ConfigParser.SafeConfigParser()
    config.read(args)

    def parse_tags(tags):
        if tags is None or tags == "":
            return None
        r = {}
        for k,v in [kv.split(":") for kv in tags.split(",")]:
            r[k] = v
        return r


    opts = {
        'pool':              config.get("condor", "pool"),
        'post_pool_status':  config.getboolean("condor", "post_pool_status"),
        'post_pool_slots':   config.get("condor", "post_pool_slots"),
        'slot_constraint':   config.get("condor", "slot_constraint"),
        'post_pool_glideins':config.getboolean("condor", "post_pool_glideins"),
        'post_pool_prio':    config.getboolean("condor", "post_pool_prio"),
        'negotiator_constraint': config.get("condor", "negotiator_constraint"),
        'prefer_accounting': config.getboolean("condor", "prefer_accounting"),
        'post_pool_jobs':    config.getboolean("condor", "post_pool_jobs"),
        'schedd_constraint': config.get("condor", "schedd_constraint"),
        'use_gsi_auth':      config.getboolean("condor", "use_gsi_auth"),
        'x509_user_key':     config.get("condor", "X509_USER_KEY"),
        'x509_user_cert':    config.get("condor", "X509_USER_CERT"),
        'use_graphite':      config.getboolean("graphite", "enable"),
        'namespace':         config.get("graphite", "namespace"),
        'meta_namespace':    config.get("graphite", "meta_namespace"),
        'graphite_host':     config.get("graphite", "host"),
        'graphite_pickle_port':     config.getint("graphite", "port"),
        'use_influxdb':      config.getboolean("influxdb", "enable"),
        'influxdb_host':     config.get("influxdb", "host"),
        'influxdb_port':     config.get("influxdb", "port"),
        'influxdb_db':       config.get("influxdb", "db"),
        'influxdb_tags':     parse_tags(config.get("influxdb", "tags")),
        'test':              cmd_opts.test or config.getboolean("probe", "test"),
        'once':              cmd_opts.once or config.getboolean("probe", "once"),
        'interval':          config.getint("probe", "interval"),
        'delay':             config.getint("probe", "delay"),
        'retries':           config.getint("probe", "retries"),
        'publish_metrics':   config.getboolean("probe", "publish_metrics"),
        'metrics_port':      cmd_opts.port,
    }

    return opts

def main():
    opts = get_options()
    if opts['test']:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO
    logging.basicConfig(level=loglevel,
            format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")

    logger.info('Probe configuraion: \n'+pprint.pformat(opts))

    probe = CondorProbe(**opts)
    probe.run()

if __name__ == '__main__':
    main()
