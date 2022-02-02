#!/usr/bin/python3

from pprint import pprint

import htcondor
import classad


def bool_stats(data, key, threshold):
    entry_count = 0 
    true_count = 0
    for entry in data:
        entry_count += 1
        if key in entry and entry[key] == True:
            true_count += 1
    percent = float(true_count) / entry_count * 100.0
    if percent < threshold:
        return '  <li>%.1d%% of the nodes have %s = True</li>\n' %(percent, key)
    return ''


coll = htcondor.Collector()

# collect the uniq ResourceNames
resource_names = []
for data in coll.query(htcondor.AdTypes.Startd,
                       constraint='DynamicSlot =!= true',
                       projection=['GLIDEIN_ResourceName']):
    if 'GLIDEIN_ResourceName' not in data:
        continue
    if data['GLIDEIN_ResourceName'] not in resource_names:
        resource_names.append(data['GLIDEIN_ResourceName'])
resource_names.sort(key=lambda s: s.lower())

html = '<h1>Potential Node Issues</h1>\n'

# for each site
for rname in resource_names:
    site_html = ''
    raw = coll.query(htcondor.AdTypes.Startd,
                     constraint='GLIDEIN_ResourceName == "%s" && DynamicSlot =!= true' % rname,
                     projection=['HAS_CVMFS_connect_opensciencegrid_org', 'HAS_CVMFS_singularity_opensciencegrid_org', 'HAS_SINGULARITY']) 

    # fill in missing values
    #for entry in raw:
    #    if 'HAS_CVMFS_connect_opensciencegrid_org' not in entry:
    #        entry['HAS_CVMFS_connect_opensciencegrid_org'] = False
 
    site_html += bool_stats(raw, 'HAS_CVMFS_connect_opensciencegrid_org', 90)
    site_html += bool_stats(raw, 'HAS_CVMFS_singularity_opensciencegrid_org', 90)
    site_html += bool_stats(raw, 'HAS_SINGULARITY', 90)

    if site_html != '':
        html += '\n<h3>%s</h3>\n <p>%d nodes reporting</p>\n <ul>\n%s </ul>\n' %(rname, len(raw), site_html)

print(html)

