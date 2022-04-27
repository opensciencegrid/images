#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A script to subscribe administrators in OSG topology to OSG status page 
"""
import os
import sys
import argparse
import syslog
import topology_utils
from status_api import StatusApi
import config
import pprint
pp = pprint.PrettyPrinter(indent=4)

status_api = StatusApi(page_id=config.page_id, api_key=config.api_key)

def get_parser():
   oparser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]),
                                      add_help=True)
   oparser.add_argument("--host", dest="host", default="my.opensciencegrid.org",
                         help="Remote topology host (default my.opensciencegrid.org)")
   oparser.add_argument("--cert", dest="cert", help="Client certificate")
   oparser.add_argument("--key", dest="key", help="Client certificate private key")
   subparsers = oparser.add_subparsers()
   #print ('parser: %s' % oparser)
   contactparsers = []
   
   list_resource_contacts_parser = \
       subparsers.add_parser('list-resource-contacts',
                             help='List OSG contacts by resource name.')
   contactparsers.append(list_resource_contacts_parser)
   #print('contactparsers:%s' % contactparsers)
   list_resource_contacts_parser.set_defaults(which="list_resource_contacts")
   list_resource_contacts_parser.add_argument( \
       "--service",
            dest="provides_service", help="Filter on resources that provide given "
           "service(s)")
   list_resource_contacts_parser.add_argument("--vo",
       dest="owner_vo", help="Filter on resources that list VO(s) as a "
       "partial owner")
   list_resource_contacts_parser.add_argument(dest="filter", action="store",
       nargs="?", help="Shell expression filter on the resource name or FQDN")
   list_resource_contacts_parser.add_argument("--fqdn", dest="fqdn", default=False, action="store_true",
       help="Treat the filter as an FQDN instead of a resource name")
   
   list_vo_contacts_parser = subparsers.add_parser('list-vo-contacts',
       help='List OSG contacts by VO name.')
   contactparsers.append(list_vo_contacts_parser)
   list_vo_contacts_parser.set_defaults(which="list_vo_contacts")
   list_vo_contacts_parser.set_defaults(fqdn=False)
   list_vo_contacts_parser.add_argument(dest="filter", action="store",
       nargs="?", help="Shell expression filter on the VO name")
   
   list_contacts_parser = subparsers.add_parser('list-contacts',
       help='List OSG resource and VO contacts.')
   contactparsers.append(list_contacts_parser)
   list_contacts_parser.set_defaults(which="list_contacts")
   list_contacts_parser.add_argument(dest="filter", action="store",
       nargs="?", help="Shell expression filter on the VO name, resource name or FQDN")
   list_contacts_parser.add_argument("--fqdn", dest="fqdn", default=False, action="store_true",
       help="Treat the filter as an FQDN instead of a resource name")

   for parser in contactparsers:
       #print ('parser: %s' % parser)       
       parser.add_argument("--type", default="all",
           dest="contact_type", help="Filter on contact type "
           "(e.g. administrative, miscellaneous, security, or submitter; "
           "default all)")
       parser.add_argument("--output", default="full",
                           dest="output_mode", help="Select the output mode "
                           "(email or full; default full)")
       parser.add_argument("--email-from-file",
                           default=None,
                           dest="email_file",
                           help="Path to file containing list of emails for contact filtering")
       #print ('parser args: %s' % parser.parse_args())
              
   return(oparser)

def get_contact_emails(args):
    results = topology_utils.get_resource_contacts(args)
    #pp.pprint(results)
    results = topology_utils.filter_contacts(args, results)
    #print(len(results))
    #pp.pprint(results)
    emails = set( contact['Email'].lower() 
                  for contact in results.values()
                  if 'Email' in contact )
    emails = sorted(emails)
    #print(emails)
    print(len(emails))
        
    return(emails)
        
    
def main():
    oparser = get_parser()

    args = oparser.parse_args()
    #pp.pprint ('args: %s' % args)
    if getattr(args, "filter") is not None:
        if args.fqdn:
            args.fqdn_filter = args.filter.strip()
        else:
            args.name_filter = args.filter.strip()

    try:
        with open(args.email_file) as f:
            contents = f.read()
            args.contact_emails = contents.split('\n')
    except TypeError:
        pass  # --email-from-file not specified
    except IOError as exc:
        sys.exit("Failed to read email file: %s" % exc)
    
    subscribed = status_api.get_subscribers(is_subscribed = True)
    subscribed_email_id_list = { i['email']]: i['id'] for i in subscribed }
    subscribed_emails = [ i['email'] for i in subscribed ]
    unsubscribed = status_api.get_subscribers(is_subscribed = False)
    unsubscribed_emails = [ i['email'] for i in unsubscribed ]
    contact_emails = get_contact_emails(args)
    
    syslog.openlog("contact_sync")
    syslog.syslog(syslog.LOG_ALERT, 'Synchronizing new contacts:')
    for item in list(set(contact_emails)-set(subscribed_emails + unsubscribed_emails)): 
        new_subscriber = status_api.new_subscriber(email=item)
        #pp.pprint(new_subscriber)
        syslog.syslog(syslog.LOG_ALERT, '%s will be subscribed' % item)
        print('%s will be subscribed' % item)
        status_api.create_a_subscriber(new_subscriber)
    syslog.closelog()

if __name__ == '__main__':
    sys.exit(main())
