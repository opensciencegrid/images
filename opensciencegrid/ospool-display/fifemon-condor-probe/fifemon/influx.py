#!/usr/bin/python
import logging
import os

from influxdb import InfluxDBClient

logger = logging.getLogger(__name__)

class Influxdb(object):
    def __init__(self, host="localhost", port=8086, db="test", username=None, password=None):
        self.host = host
        self.port = port
        if username is None:
            username=os.getenv('INFLUXDB_USERNAME')
        if password is None:
            password=os.getenv('INFLUXDB_PASSWORD')

        self.client = InfluxDBClient(host, port, username, password, db)

    def send_metric(self, measurement, value, tags={}, timestamp=None, field="value"):
        point = {
                "measurement": measurement,
                "tags": tags,
                "fields": {field: value},
                }
        if timestamp is not None:
            point['time'] = timestamp
        self.client.write_points([point])

    def send_metrics(self, data, tags={}):
        self.client.write_points(data,tags=tags)

    def send_dict(self, data, send_data=True, timestamp=None, schema=None, field="value", tags={}):
        if data is None or len(data) == 0:
            logger.warning("send_dict called with no data")
            return
        points = []
        if schema is None:
            logger.warning("no schema provided, sending complete metric as measurement")
            for k,v in data.iteritems():
                points.append({
                    "measurement": k,
                    "fields": {field: v},
                    })
        else:
            schema_parts = schema.split(".")
            for k,v in data.iteritems():
                parts = k.split(".")
                if len(parts) != len(schema_parts):
                    logger.error("metric '{metric}' does not match schema '{schema}', skipping".format(
                        metric=k,
                        schema=schema))
                point = {
                        "measurement": None,
                        "tags": {},
                        "fields": {field: v},
                        }
                for i in xrange(len(parts)):
                    if schema_parts[i] == "measurement":
                        point["measurement"] = parts[i]
                    elif schema_parts[i] != "_":
                        point["tags"][schema_parts[i]] = parts[i]
                logger.debug("sending point %s"%point)
                points.append(point)
        logger.debug("sending points with tags %s"%tags)
        if send_data:
            self.client.write_points(points,tags=tags)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    g = Influxdb()
    g.send_metric('jobs', 2345, tags={'cluster':'fifebatch','user':'bob'})
