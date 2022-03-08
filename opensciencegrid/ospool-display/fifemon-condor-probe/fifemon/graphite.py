#!/usr/bin/python
import logging
import time
import cPickle
import struct
import socket
import sys

logger = logging.getLogger(__name__)

def sanitize_key(key):
    if key is None:
        return key
    replacements = {
            ".": "_",
            " ": "_",
    }
    for old,new in replacements.iteritems():
        key = key.replace(old, new)
    return key

class Graphite(object):
    def __init__(self,host="localhost",pickle_port=2004):
        self.graphite_host = host
        self.graphite_pickle_port = pickle_port

    def send_dict(self,namespace, data, send_data=True, timestamp=None, batch_size=1000):
        """send data contained in dictionary as {k: v} to graphite dataset
        $namespace.k with current timestamp"""
        if data is None:
            logger.warning("send_dict called with no data")
            return
        if timestamp is None:
            timestamp=time.time()
        post_data=[]
        # turning data dict into [('$path.$key',($timestamp,$value)),...]]
        for k,v in data.iteritems():
            t = (namespace+"."+k, (timestamp, v))
            post_data.append(t)
            logger.debug(str(t))
        for i in xrange(len(post_data)//batch_size + 1):
            # pickle data
            payload = cPickle.dumps(post_data[i*batch_size:(i+1)*batch_size], protocol=2)
            header = struct.pack("!L", len(payload))
            message = header + payload
            # throw data at graphite
            if send_data:
                s=socket.socket()
                try:
                    s.connect( (self.graphite_host, self.graphite_pickle_port) )
                    s.sendall(message)
                except socket.error as e:
                    logger.error("unable to send data to graphite at %s:%d\n" % (self.graphite_host,self.graphite_pickle_port))
                finally:
                    s.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    data = {'count1': 5, 'count2': 0.5}
    g = Graphite()
    g.send_dict('test',data,send_data=False)
