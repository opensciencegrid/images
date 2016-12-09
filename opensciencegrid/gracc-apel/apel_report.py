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

vo_list = ['atlas','alice','cms','enmr.eu']

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
        ]
    )

    bkt = s.aggs
    bkt = bkt.bucket('Cores',          'terms', field='Processors')
    bkt = bkt.bucket('VO',             'terms', field='ReportableVOName')
    bkt = bkt.bucket('GlobalUsername', 'terms', field='DN')
    bkt = bkt.bucket('Site',           'terms', field='ResourceGroup')
    #bkt = bkt.bucket('Site',          'terms', field='SiteName')
    #bkt = bkt.bucket('Site',          'terms', field='WLCGAccountingName')

    bkt = bkt.metric('WallDuration',       'sum', field='WallDuration')
    bkt = bkt.metric('CpuDuration_system', 'sum', field='CpuDuration_system')
    bkt = bkt.metric('CpuDuration_user',   'sum', field='CpuDuration_user')
    bkt = bkt.metric('CoreHours',          'sum', field='CoreHours')
    bkt = bkt.metric('NumberOfJobs',       'sum', field='Count')
    bkt = bkt.metric('EarliestEndTime',    'min', field='EndTime')
    bkt = bkt.metric('LatestEndTime',      'max', field='EndTime')

    #bkt = bkt.metric('CoreHours', 'sum', field='CoreHours')

    response = s.execute()
    return response

# Fixed entries:
fixed_header = "APEL-summary-job-message: v0.3"
fixed_separator = "%%"
fixed_infrastructure = "Gratia-OSG"
fixed_nodecount = 1
fixed_normalizationfactor = 12

def print_header():
    print fixed_header

def print_record(year, month, vo, site, cores, dn, bkt):
    walldur = int(bkt.WallDuration.value)
    corewalldur = walldur * cores
    cpudur = int(bkt.CpuDuration_user.value + bkt.CpuDuration_system.value)
    nf = fixed_normalizationfactor

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
    print "WallDuration:",           corewalldur
    print "CpuDuration:",            cpudur
    print "NormalisedWallDuration:", int(corewalldur * nf)
    print "NormalisedCpuDuration:",  int(cpudur * nf)
    print "NumberOfJobs:",           int(bkt.NumberOfJobs.value)
    print fixed_separator

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

