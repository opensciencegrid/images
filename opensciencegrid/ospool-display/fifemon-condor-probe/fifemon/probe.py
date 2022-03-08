#!/usr/bin/python
import logging
import time

logger = logging.getLogger(__name__)

class Probe(object):
    def __init__(self, *args, **kwargs):
        self.interval = kwargs.pop('interval', 240)
        self.retries = kwargs.pop('retries', 10)
        self.delay = kwargs.pop('delay', 30)
        self.test = kwargs.pop('test',True)
        self.once = self.test or kwargs.pop('once',False)

        self.use_graphite = kwargs.pop('use_graphite',True)
        self.graphite_host = kwargs.pop('graphite_host','localhost')
        self.graphite_pickle_port = kwargs.pop('graphite_pickle_port',2004)
        self.namespace = kwargs.pop('namespace', 'test')
        self.meta_namespace = kwargs.pop('meta_namespace', 'probes.test')

        self.use_influxdb = kwargs.pop('use_influxdb',False)
        self.influxdb_host = kwargs.pop('influxdb_host','localhost')
        self.influxdb_port = kwargs.pop('influxdb_port',8086)
        self.influxdb_db = kwargs.pop('influxdb_db','test')
        self.influxdb_tags = kwargs.pop('influxdb_tags',{})

        self.publish_metrics = kwargs.pop('publish_metrics',True)
        self.metrics_port = kwargs.pop('metrics_port',8100)

        if self.test:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)

        if self.use_graphite:
            from graphite import Graphite
            self.graphite = Graphite(self.graphite_host, self.graphite_pickle_port)
        if self.use_influxdb:
            from influx import Influxdb
            self.influxdb = Influxdb(self.influxdb_host, self.influxdb_port, self.influxdb_db)
        if self.publish_metrics:
            import prometheus_client as prom
            self.last_runtime_metric = prom.Gauge('probe_runtime_seconds',
                    'Probe last runtime')
            self.interval_metric = prom.Gauge('probe_interval_seconds',
                    'Probe run interval')
            self.interval_metric.set(self.interval)
            self.status_metric = prom.Gauge('probe_status',
                    'Probe is running (1) or sleeping (0)')
            prom.start_http_server(self.metrics_port)

    def __unicode__(self):
        return """
namespace:      %s
meta_namespace: %s
interval:       %d s
retries:        %d
delay:          %d s
test:           %s
once:           %s

use_graphite:   %s
graphite_host:  %s
graphite_pickle_port:  %s

use_influxdb:   %s
influxdb_host:  %s
influxdb_port:  %d
influxdb_db:    %d

publish_metrics: %s
metrics_port:   %d

""" % (self.namespace,
        self.meta_namespace,
        self.interval,
        self.retries,
        self.delay,
        self.test,
        self.once,
        self.use_graphite,
        self.graphite_host,
        self.graphite_pickle_port,
        self.use_influxdb,
        self.influxdb_host,
        self.influxdb_port,
        self.influxdb_db,
        self.publish_metrics,
        self.metrics_port)

    def __str__(self):
        return self.__unicode__()

    def post(self):
        pass

    def run(self):
        while True:
            start = time.time()
            if self.publish_metrics:
                self.status_metric.set(1)
            self.post()
            duration = time.time()-start
            if self.publish_metrics:
                self.status_metric.set(0)
                self.last_runtime_metric.set(duration)
            logger.info("({0}) posted data in {1} s".format(self.namespace, duration))
            meta_data = {
                    "update_time": duration,
                    "update_interval": self.interval,
                    "duty_cycle": duration/self.interval,
                    }
            if self.use_graphite:
                self.graphite.send_dict(self.meta_namespace, meta_data, send_data = (not self.test))
            if self.use_influxdb:
                pass
            sleep = max(self.interval-duration-10,0)
            logger.info("({0}) sleeping {1} s".format(self.namespace,sleep))
            if self.test or self.once:
                return
            time.sleep(sleep)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    p = Probe(test=True)
    logger.debug(p)
    p.run()
