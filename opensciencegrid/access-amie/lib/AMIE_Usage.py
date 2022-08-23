#!/usr/bin/python3

import datetime
import glob
import logging
import os

from amieclient import UsageClient
from amieclient.packet import Packet

log = logging.getLogger('osgxsede')


class AMIE_Usage:
    client = None
    config = None

    def __init__(self, config):
        self.config = config
        self.client = UsageClient(site_name='OSG',
                                 usage_url='https://usage.xsede.org/api/v1',
                                 api_key=self.config['amie']['api_key'])

    def get_failed_records(self):
        return self.client.get_failed_records()

    def send(self, packet):
        # we are not keeping copies of usage packets
        return self.client.send(packet)
    
    def status(self, start_t, end_t):
        return self.client.status(from_time=start_t, to_time=end_t)
