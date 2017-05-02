#!/usr/bin/python

import elasticsearch
from elasticsearch_dsl import Search, A, Q
#import logging
import datetime
import dateutil.relativedelta
import operator
import sys
import os


#logging.basicConfig(level=logging.WARN)
es = elasticsearch.Elasticsearch(
        ['https://gracc.opensciencegrid.org/q'],
        timeout=300, use_ssl=True, verify_certs=True,
        ca_certs='/etc/ssl/certs/ca-bundle.crt')

osg_raw_index = 'gracc.osg.raw-*'
osg_summary_index = 'gracc.osg.summary'

vo_list = ['atlas', 'alice', 'cms', 'enmr.eu']

MAXSZ=2**30
MISSING='__MISSING__'

def add_bkt_metrics(bkt):
    bkt = bkt.metric('NormalFactor','terms', field='OIM_WLCGAPELNormalFactor')
    bkt = bkt.metric('CpuDuration_system', 'sum', field='CpuDuration_system')
    bkt = bkt.metric('CpuDuration_user',   'sum', field='CpuDuration_user')
    bkt = bkt.metric('WallDuration',       'sum', field='WallDuration')
    bkt = bkt.metric('NumberOfJobs',       'sum', field='Count')
    bkt = bkt.metric('EarliestEndTime',    'min', field='EndTime')
    bkt = bkt.metric('LatestEndTime',      'max', field='EndTime')
    return bkt

def gracc_query_apel(year, month):
    index = osg_summary_index
    starttime = datetime.datetime(year, month, 1)
    endymd = (year, month+1, 1) if month < 12 else (year+1, 1, 1)
    endtime = datetime.datetime(*endymd)
    s = Search(using=es, index=index)
    s = s.query('bool',
        filter=[
            Q('range', EndTime={'gte': starttime, 'lt': endtime })
          & Q('terms', VOName=vo_list)
          & ( Q('term', ResourceType='Batch') | Q('term', Grid='Local')) )
        ]
    )

    bkt = s.aggs
    bkt = bkt.bucket('Cores', 'terms', size=MAXSZ, field='Processors')
    bkt = bkt.bucket('VO',    'terms', size=MAXSZ, field='VOName')
    bkt = bkt.bucket('DN',    'terms', size=MAXSZ, field='DN')
    bkt = bkt.bucket('Site',  'terms', size=MAXSZ, missing=MISSING, field='OIM_ResourceGroup')
    #bkt = bkt.bucket('Site', 'terms', size=MAXSZ, field='SiteName')
    #bkt = bkt.bucket('Site', 'terms', size=MAXSZ, field='WLCGAccountingName')
    add_bkt_metrics(bkt)

    bkt = bkt.bucket('SiteName',  'terms', size=MAXSZ, field='SiteName')

    add_bkt_metrics(bkt)

    response = s.execute()
    return response

# Fixed entries:
fixed_header = "APEL-summary-job-message: v0.3"
fixed_separator = "%%"
fixed_infrastructure = "Gratia-OSG"
fixed_nodecount = 1
fixed_normalizationfactor = 12

def normal_hepspec_table():
    from os.path import join, dirname, abspath
    normal_hepspec_path = join(dirname(abspath(__file__)), "normal_hepspec")
    table = {}
    for line in open(normal_hepspec_path):
        if line.startswith('#'):
            continue
        tokens = line.split()
        if len(tokens) != 2:
            continue
        site, nf = tokens
        nf = float(nf)
        table[site] = nf
    return table

nf_table = normal_hepspec_table()

def norm_factor(bkt, site):
    nf_max = 200
    nf_default = 12
    nf_values = [ b.key for b in bkt.NormalFactor.buckets if b.key > 0 ]
    if len(nf_values) == 0:
        # XXX: *should* look up from table here, but the old script just
        #      used the default (12) when not found on OIM.
        # TODO: log
        nf = nf_default
    elif len(nf_values) == 1:
        # ok, normal case
        nf = nf_values[0]
    else:
        # oh weird, why more than one norm factor here?
        # TODO: log
        nf = 1.0 * sum(nf_values) / len(nf_values)

    if nf >= nf_max:
        # out of range: do table lookup
        # TODO: log
        if site in nf_table:
            # TODO: log
            nf = nf_table[site]
        else:
            # TODO: log
            nf = nf_default
    return nf

from collections import namedtuple, defaultdict

class autodict(defaultdict):
    def __init__(self,*other):
        defaultdict.__init__(self, self.__class__, *other)
    def __add__ (self, other):
        return other
    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, dict.__repr__(self))

RecordKey = namedtuple('RecordKey', ['vo', 'site', 'cores', 'dn'])
Record = namedtuple('Record', ["mintime", "maxtime", "walldur", "cpudur",
                               "nf", "njobs"])

def bkt_record(bkt, site):
    mintime = int(bkt.EarliestEndTime.value / 1000)
    maxtime = int(bkt.LatestEndTime.value / 1000)
    walldur = int(bkt.WallDuration.value)
    cpudur  = int(bkt.CpuDuration_user.value + bkt.CpuDuration_system.value)
    nf      = norm_factor(bkt, site)
    njobs   = int(bkt.NumberOfJobs.value)
    return Record(mintime, maxtime, walldur, cpudur, nf, njobs)

def record_adder(a,b):
    mintime = min(a.mintime, b.mintime)
    maxtime = max(a.maxtime, b.maxtime)
    walldur = a.walldur + b.walldur
    cpudur  = a.cpudur  + b.cpudur
    nf      = min(a.nf, b.nf)
    njobs   = a.njobs + b.njobs
    return Record(mintime, maxtime, walldur, cpudur, nf, njobs)

Record.__add__ = record_adder

site_map = {
    'Crane':     'Nebraska',
    'Sandhills': 'Nebraska',
    'Tusker':    'Nebraska'
}

def add_record(recs, vo, site, cores, dn, bkt):
    if site in site_map:
        site = site_map[site]

    rk  = RecordKey(vo, site, cores, dn)
    rec = bkt_record(bkt, site)

    recs[rk] += rec

def print_header():
    print fixed_header

def print_rk_recr(year, month, rk, rec):

    if rk.dn == "N/A":
        dn = "generic %s user" % rk.vo
    else:
        dn = rk.dn

    print "Site:",                   rk.site
    print "VO:",                     rk.vo
    print "EarliestEndTime:",        rec.mintime
    print "LatestEndTime:",          rec.maxtime
    print "Month:",                  "%02d" % month
    print "Year:",                   year
    print "Infrastructure:",         fixed_infrastructure
    print "GlobalUserName:",         dn
    print "Processors:",             rk.cores
    print "NodeCount:",              fixed_nodecount
    print "WallDuration:",           rec.walldur
    print "CpuDuration:",            rec.cpudur
    print "NormalisedWallDuration:", int(rec.walldur * rec.nf)
    print "NormalisedCpuDuration:",  int(rec.cpudur  * rec.nf)
    print "NumberOfJobs:",           rec.njobs
    print fixed_separator

def bkt_key_lower(bkt):
    return bkt.key.lower()

def sorted_buckets(agg, key=operator.attrgetter('key')):
    return sorted(agg.buckets, key=key)

def auto_year_month():
    today = datetime.datetime.today()
    if today.day < 3:
        onemonth = dateutil.relativedelta.relativedelta(months=1)
        lastmonth = today - onemonth
        return lastmonth.year, lastmonth.month
    else:
        return today.year, today.month

def main():
    if len(sys.argv[1:]) == 0:
        year,month = auto_year_month()
    else:
        try:
            year,month = map(int, sys.argv[1:])
        except:
            print >>sys.stderr, \
                  "usage: %s [YEAR MONTH]" % os.path.basename(__file__)
            sys.exit(0)

    orig_stdout = sys.stdout
    outfile = "%02d_%d.apel" % (month, year)
    sys.stdout = open(outfile, "w")

    resp = gracc_query_apel(year, month)
    aggs = resp.aggregations

    recs = autodict()

    print_header()
    for cores_bkt in sorted_buckets(aggs.Cores):
        cores = cores_bkt.key
        for vo_bkt in sorted_buckets(cores_bkt.VO):
            vo = vo_bkt.key
            for dn_bkt in sorted_buckets(vo_bkt.DN):
                dn = dn_bkt.key
                for site_bkt in sorted_buckets(dn_bkt.Site):
                    site = site_bkt.key
                    if site == MISSING:
                        for sitename_bkt in sorted_buckets(site_bkt.SiteName):
                            sitename = sitename_bkt.key
                            add_record(recs, vo, sitename, cores, dn,
                                       sitename_bkt)
                    else:
                        add_record(recs, vo, site, cores, dn, site_bkt)

    for rk,rec in sorted(recs.items()):
        print_rk_recr(year, month, rk, rec)

    sys.stdout = orig_stdout
    print "wrote: %s" % outfile

if __name__ == '__main__':
    main()

