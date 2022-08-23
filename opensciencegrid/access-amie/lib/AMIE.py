#!/usr/bin/python3

import datetime
import glob
import logging
import os

from amieclient import AMIEClient
from amieclient.packet import Packet

log = logging.getLogger('accessamie')


class AMIE:
    client = None
    config = None

    def __init__(self, config):
        self.config = config
        self.client = AMIEClient(site_name='OSG',
                                 amie_url=self.config['amie']['url'],
                                 api_key=self.config['amie']['api_key'])

        dir = self.config['main']['state_dir']

        self.dir_incoming_received = '{}/xfer/incoming/received'.format(dir)
        os.makedirs(self.dir_incoming_received, exist_ok=True)

        self.dir_incoming_parked = '{}/xfer/incoming/parked'.format(dir)
        os.makedirs(self.dir_incoming_parked, exist_ok=True)

        self.dir_outgoing_sent = '{}/xfer/outgoing/sent'.format(dir)
        os.makedirs(self.dir_outgoing_sent, exist_ok=True)

    def packet_filename(self, packet):
        packet_type = packet.packet_type
        packet_rec_id = packet.packet_rec_id
        trans_rec_id = packet.trans_rec_id
        return '{}-{}-{}.json'.format(packet_type, trans_rec_id, packet_rec_id)

    def list(self):
        packets = self.client.list_packets().packets
        return packets

    def already_processed(self, packet):
        # check incoming directories
        fn = self.packet_filename(packet)
        if os.path.exists(os.path.join(self.dir_incoming_received, fn)):
            return True
        if os.path.exists(os.path.join(self.dir_incoming_parked, fn)):
            return True
        return False

    def load_packets(self, direction, subdir):
        state_dir = self.config['main']['state_dir']
        results = []
        for fname in glob.glob('{}/xfer/{}/{}/*.json'.format(state_dir, direction, subdir)):
            with open(fname) as f:
                # packet = RequestProjectCreate().from_json(f.read())
                packet = Packet().from_json(f.read())
            results.append(packet)
        return results

    def save_packet(self, packet, direction, subdir):
        state_dir = self.config['main']['state_dir']
        fn = self.packet_filename(packet)
        fullname = '{}/xfer/{}/{}/{}'.format(state_dir, direction, subdir, fn)
        with open(fullname, 'w') as f:
            f.write(packet.json(indent=4, sort_keys=True))

    def send_packet(self, packet):
        log.info("Sending packet: type={} packet_rec_id={} trans_rec_id={}".format(
            packet.packet_type, packet.packet_rec_id, packet.trans_rec_id
        ))
        # make sure the packet has a valid packet_timestamp
        self.client.send_packet(packet)
        if packet._packet_timestamp is None:
            packet._packet_timestamp = datetime.datetime.utcnow()
        self.save_packet(packet, 'outgoing', 'sent')

    def unpark(self, packet):
        # we already keep a copy in incoming/received/
        fn = self.packet_filename(packet)
        os.unlink(os.path.join(self.dir_incoming_parked, fn))
