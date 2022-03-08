#!/usr/bin/env python
import logging
import pprint
import traceback

import htcondor

from fifemon.condor_probe import CondorProbe, get_options

logger = logging.getLogger(__name__)

def get_lpc_node_boundary(coll):
    """
    query the negotiator for the boundary node number for the LPC-allocated nodes,
    and return a constraint that limits the startds queried to those nodes.
    """
    bound=1900
    try:
        ads = coll.query(htcondor.AdTypes.Negotiator,
                         'regexp("CMSLPC",Name)',
                         ['FERMIHTC_LPC_MAX_WN_NUM'])
        assert len(ads) == 1
        assert 'FERMIHTC_LPC_MAX_WN_NUM' in ads[0]
        bound = int(ads[0]['FERMIHTC_LPC_MAX_WN_NUM'])
    except Exception as e:
        logger.error('trouble getting LPC node boundary, using default %d:'%(bound))
        traceback.print_exc()
    return 'FERMIHTC_NODE_NUMBER < %d && regexp("slot1",Name)' % (bound)

def add_lpc_options(opts):
    # by setting the constraint to a function it will get called by the probe at query time
    opts['slot_constraint'] =  get_lpc_node_boundary
    opts['schedd_constraint'] = 'regexp("lpc",Name)'
    opts['negotiator_constraint'] = 'regexp("CMSLPC",Name)'
    return opts

if __name__ == '__main__':
    opts = add_lpc_options(get_options())
    if opts['test']:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO
    logging.basicConfig(level=loglevel,
            format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")

    logger.info('Probe configuraion: \n'+pprint.pformat(opts))

    probe = CondorProbe(**opts)
    probe.run()
