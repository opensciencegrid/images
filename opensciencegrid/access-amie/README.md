# osg-xsede-amie

This is a tool for synchronizing data from ACCESS AMIE to OSGConnect. Some of the AMIE
documentation is internal but a few pointers for overview:

 * amieclient is used as a higher level interface for the AMIE REST API. 
   [Github repo](https://github.com/XSEDE/amieclient) /
   [Documentation](https://xsede.github.io/amieclient/)

 * [OSGConnect API](https://github.com/maniaclab/ci-connect-api). The schema
   is described [here](https://github.com/maniaclab/ci-connect-api/tree/master/resources/api_specification)

 * [Freshdesk API](https://developer.freshdesk.com/api/v1/)

 * [GRACC](https://indico.fnal.gov/event/20809/contributions/59310/attachments/37160/45212/20190930-GRACC.pdf) is the source for the usage records

## Configuration

The tool is intended for deployment in one of the OSG K8s instances. It is assumed
that `/opt/access-amie/etc/access-amie.conf` is bind-mounted from a
K8s secret. A skeleton example is:

```
[main]

debug = False
state_dir = /var/lib/access-amie

[amie]

url = 
api_key = 

[connect]

url = 
token = 

[freshdesk]

url = 
api_key = 
opened_by_email = 

[gracc]

url = https://gracc.opensciencegrid.org/q

[graccusage_osgconnect]

probe = *osgconnect.net

```

`graccusage_*` sections can be added for more special GRACC to XSEDE project
mappings.


