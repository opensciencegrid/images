#!/usr/bin/python

import elasticsearch
from elasticsearch_dsl import Search, A, Q
#import logging
import datetime
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

def gracc_query_apel(year, month):
    index = osg_summary_index
    s = Search(using=es, index=index)
    starttime = datetime.datetime(year, month, 1)
    endymd = (year, month+1, 1) if month < 12 else (year+1, 1, 1)
    endtime = datetime.datetime(*endymd)
    s = s.query('bool',
        filter=[
            Q('range', EndTime={'gte': starttime, 'lt': endtime })
          & Q('terms', ReportableVOName=vo_list)
          & Q('term',  ResourceType='Batch')
        ]
    )

    MAXSZ=2**30

    bkt = s.aggs
    bkt = bkt.bucket('Cores', 'terms', size=MAXSZ, field='Processors')
    bkt = bkt.bucket('VO',    'terms', size=MAXSZ, field='ReportableVOName')
    bkt = bkt.bucket('GlobalUsername', 'terms', size=MAXSZ, field='DN')
    bkt = bkt.bucket('Site',  'terms', size=MAXSZ, field='OIM_ResourceGroup')
    #bkt = bkt.bucket('Site', 'terms', size=MAXSZ, field='SiteName')
    #bkt = bkt.bucket('Site', 'terms', size=MAXSZ, field='WLCGAccountingName')

    bkt = bkt.metric('NormalFactor','terms', field='OIM_WLCGAPELNormalFactor')
    bkt = bkt.metric('CpuDuration_system', 'sum', field='CpuDuration_system')
    bkt = bkt.metric('CpuDuration_user',   'sum', field='CpuDuration_user')
    bkt = bkt.metric('WallDuration',       'sum', field='WallDuration')
    bkt = bkt.metric('NumberOfJobs',       'sum', field='Count')
    bkt = bkt.metric('EarliestEndTime',    'min', field='EndTime')
    bkt = bkt.metric('LatestEndTime',      'max', field='EndTime')

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
    nf_buckets = bkt.NormalFactor.buckets
    if len(nf_buckets) == 0:
        # XXX: *should* look up from table here, but the old script just
        #      used the default (12) when not found on OIM.
        # TODO: log
        nf = nf_default
    elif len(nf_buckets) == 1:
        # ok, normal case
        nf = nf_buckets[0].key
    else:
        # oh weird, why more than one norm factor here?
        # TODO: log
        nf = 1.0 * sum(b.key for b in nf_buckets) / len(nf_buckets)

    if not ( 0 < nf < nf_max ):
        # out of range: do table lookup
        # TODO: log
        if site in nf_table:
            # TODO: log
            nf = nf_table[site]
        else:
            # TODO: log
            nf = nf_default
    return nf

def print_header():
    print fixed_header

def print_record(year, month, vo, site, cores, dn, bkt):
    cpudur = int(bkt.CpuDuration_user.value + bkt.CpuDuration_system.value)
    walldur = int(bkt.WallDuration.value)
    nf = norm_factor(bkt, site)

    if dn == "N/A":
        dn = "generic %s user" % vo

    print "Site:",                   site
    print "VO:",                     vo
    print "EarliestEndTime:",        int(bkt.EarliestEndTime.value / 1000)
    print "LatestEndTime:",          int(bkt.LatestEndTime.value / 1000)
    print "Month:",                  "%02d" % month
    print "Year:",                   year
    print "Infrastructure:",         fixed_infrastructure
    print "GlobalUserName:",         dn
    print "Processors:",             cores
    print "NodeCount:",              fixed_nodecount
    print "WallDuration:",           walldur
    print "CpuDuration:",            cpudur
    print "NormalisedWallDuration:", int(walldur * nf)
    print "NormalisedCpuDuration:",  int(cpudur * nf)
    print "NumberOfJobs:",           int(bkt.NumberOfJobs.value)
    print fixed_separator

def bkt_key_lower(bkt):
    return bkt.key.lower()

def sorted_buckets(agg, key=operator.attrgetter('key')):
    return sorted(agg.buckets, key=key)

def main():
    try:
        year,month = map(int, sys.argv[1:])
    except:
        print "usage: %s YEAR MONTH" % os.path.basename(__file__)
        sys.exit(0)
    resp = gracc_query_apel(year, month)
    aggs = resp.aggregations

    print_header()
    for cores_bkt in sorted_buckets(aggs.Cores):
        cores = cores_bkt.key
        for vo_bkt in sorted_buckets(cores_bkt.VO):
            vo = vo_bkt.key
            for dn_bkt in sorted_buckets(vo_bkt.GlobalUsername):
                dn = dn_bkt.key
                for site_bkt in sorted_buckets(dn_bkt.Site):
                    site = site_bkt.key
                    print_record(year, month, vo, site, cores, dn, site_bkt)


if __name__ == '__main__':
    main()

