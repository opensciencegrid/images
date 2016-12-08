#!/usr/bin/python

import elasticsearch
from elasticsearch_dsl import Search, A, Q
#import logging
import datetime
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
    bkt = bkt.bucket('Site',           'terms', field='SiteName')
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
header = "APEL-summary-job-message: v0.3"
separator = "%%"
infrastructure = "Gratia-OSG"
nodecount = 1
normalizationfactor = 1

def print_header():
    print header

def print_record(vo, cores, dn, site, corewalldur, cpudur, nf,
                 count, year, month, mintime, maxtime):
    print "Site:", site
    print "VO:", vo
    print "EarliestEndTime:", mintime
    print "LatestEndTime:", maxtime
    print "Month:", month
    print "Year:", year
    print "Infrastructure:", infrastructure
    print "GlobalUserName:", dn
    print "Processors:", cores
    print "NodeCount:", nodecount
    print "WallDuration:", corewalldur
    print "CpuDuration:", cpudur
    print "NormalisedWallDuration:", int(corewalldur * nf)
    print "NormalisedCpuDuration:", int(cpudur * nf)
    print "NumberOfJobs:", count
    print separator

def main():
    try:
        year,month = map(int, sys.argv[1:])
    except:
        print "usage: %s YEAR MONTH" % os.path.basename(__file__)
        sys.exit(0)
    resp = gracc_query_apel(year, month)
    aggs = resp.aggregations
    for cores_bkt in aggs.Cores.buckets:
        cores = cores_bkt.key
        for vo_bkt in cores_bkt.VO.buckets:
            vo = vo_bkt.key
            for dn_bkt in vo_bkt.GlobalUsername.buckets:
                dn = dn_bkt.key
                for site_bkt in dn_bkt.Site.buckets:
                    site = site_bkt.key
                    walldur = int(site_bkt.WallDuration.value)
                    corewalldur = walldur * cores
                    cpudur = int(site_bkt.CpuDuration_user.value + \
                                 site_bkt.CpuDuration_system.value)
                    count = int(site_bkt.NumberOfJobs.value)
                    mintime = int(site_bkt.EarliestEndTime.value)
                    maxtime = int(site_bkt.LatestEndTime.value)
                    print_record(vo, cores, dn, site, corewalldur, cpudur,
                                 normalizationfactor, count, year, month,
                                 mintime, maxtime)

if __name__ == '__main__':
    main()

