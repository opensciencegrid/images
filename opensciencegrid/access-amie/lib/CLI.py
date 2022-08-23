#!/usr/bin/python3

import argparse
import configparser
import logging
import sys
from logging.config import dictConfig

from amieclient.packet import NotifyPersonIDs

from AMIE import AMIE
from OSGConnect import OSGConnect

log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "fmt": "%(levelprefix)s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",

        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {
        "accessamie": {"handlers": ["default"], "level": "DEBUG"},
    }
}

dictConfig(log_config)
log = logging.getLogger('accessamie')

config = None
amie = None
connect = None


def main():
    global config
    global amie
    global connect

    # set up our config and other objects
    config = configparser.ConfigParser()
    config.read('/opt/access-amie/etc/access-amie.conf')
    amie = AMIE(config)
    connect = OSGConnect(config)

    parser = argparse.ArgumentParser(prog='access-amie')
    # parser.add_argument('--foo', action='store_true', help='foo help')
    subparsers = parser.add_subparsers(help='sub-command help')

    # create the parser for the "project-created" command
    parser_pcreated = subparsers.add_parser('project-created',
                                            help='Use this when a ACCESS requested project and PI has been set up in OSGConnect')
    parser_pcreated.add_argument('--project', required=True, help='Project in the form of TG-XXXXXXXX')
    parser_pcreated.add_argument('--pi-username', required=True, help='OSGConnect username of the PI')
    parser_pcreated.set_defaults(func=project_created)

    # create the parser for the "account-created" command
    parser_acreated = subparsers.add_parser('account-created',
                                            help='Use this when a ACCESS requested user account been set up in OSGConnect')
    parser_acreated.add_argument('--global-id', required=True, help='ACCESS Global ID')
    parser_acreated.add_argument('--project', required=True, help='Project in the form of TG-XXXXXXXX')
    parser_acreated.add_argument('--username', required=True, help='OSGConnect username')
    parser_acreated.set_defaults(func=account_created)

    # create the parser for the "account-move" command
    parser_amove = subparsers.add_parser('account-move',
                                         help='Move an existing account to a new OSGConnect uid/username')
    parser_amove.add_argument('--access-person-id', required=True, help='ACCESS global person id')
    parser_amove.add_argument('--connect-username', required=True, help='Target user in OSGConnect')
    parser_amove.set_defaults(func=account_move)

    # create the parser for the "account-park" command
    parser_apark = subparsers.add_parser('account-park',
                                         help='Park an old account as non-active')
    parser_apark.add_argument('--access-person-id', required=True, help='ACCESS person id')
    parser_apark.add_argument('--access-username', required=True, help='ACCESS username')
    parser_apark.set_defaults(func=account_park)

    args = parser.parse_args()
    # call the right sub function
    args.func(args)


def project_created(args):
    # Ensure that the project and user exists in OSGConnect, we have
    # a corresponding parked AMIE rpc packet, and if so send the
    # notify_project_create package to AMIE

    try:
        project = connect.project(args.project)
        pi = connect.user(args.pi_username)
        uid = pi['unix_id']
        # for testing - how should we switch to this?
        # uid = re.sub('foo', '', args.pi_username)
    except Exception as e:
        log.exception(e)
        sys.exit(1)

    # find the parked packet
    rpc = None
    for packet in amie.load_packets('incoming', 'parked'):
        p = 'TG-{}'.format(packet.GrantNumber)
        if p == args.project:
            rpc = packet
            break

    if rpc is None:
        raise RuntimeError('Unable to find a corresponding rpc packet in incoming/parked')

    # construct a NotifyProjectCreate(NPC) packet.
    npc = rpc.reply_packet()
    npc.ProjectID = args.project  # local project ID
    npc.PiPersonID = uid  # local person ID for the pi
    npc.PiRemoteSiteLogin = args.pi_username  # local username

    # send the NPC
    amie.send_packet(npc)

    # clear the parked status
    amie.unpark(rpc)


def account_created(args):
    # Ensure that the user exists in OSGConnect, we have
    # a corresponding parked AMIE rac packet, and if so send the
    # notify_account_create package to AMIE

    try:
        project = connect.project(args.project)
        pi = connect.user(args.username)
        uid = pi['unix_id']
        # for testing - how should we switch to this?
        # uid = re.sub('foo', '', args.username)
    except Exception as e:
        log.exception(e)
        sys.exit(1)

    # find the parked packet
    rac = None
    for packet in amie.load_packets('incoming', 'parked'):
        try:
            gid = packet.UserGlobalID
            p = 'TG-{}'.format(packet.GrantNumber)
            # do we need to check packet type?
            if gid == args.global_id and p == args.project:
                rac = packet
                break
        except Exception as e:
            pass

    if rac is None:
        raise RuntimeError('Unable to find a corresponding rac packet in incoming/parked')

    # construct a NotifyAccountCreate(NAC) packet.
    nac = rac.reply_packet()
    nac.ProjectID = args.project  # local project ID
    nac.UserPersonID = uid  # local person ID for the pi
    nac.UserRemoteSiteLogin = args.username  # local username

    # send the NPC
    amie.send_packet(nac)

    # clear the parked status
    amie.unpark(rac)


def account_move(args):
    # Ensure the new uid/username exist in OSGConnect. No verification
    # on the old uid.

    try:
        user = connect.user(args.connect_username)
    except Exception as e:
        log.exception(e)
        sys.exit(1)

    # construct a NotifyPersonIDs packet.
    npi = NotifyPersonIDs(
        originating_site_name="OSG"
    )
    npi.PersonID = args.access_person_id
    npi.PrimaryPersonID = user['unix_id']
    npi.PersonIdList = [user['unix_id']]
    # remove old ones
    npi.RemoveResourceList = ['grid1.osg.xsede']
    npi.ResourceLogin = [{
        'Resource': 'grid1.osg.xsede',
        'Login': user['unix_name'],
        'UID': user['unix_id']
    }]

    # send the NPI
    amie.send_packet(npi)

    log.info("Notification sent to ACCESS database")


def account_park(args):

    # construct a NotifyPersonIDs packet.
    npi = NotifyPersonIDs(
        originating_site_name="OSG"
    )
    npi.PersonID = args.access_person_id
    npi.PrimaryPersonID = args.access_username
    npi.PersonIdList = [args.access_username]
    # remove old ones
    npi.RemoveResourceList = ['grid1.osg.xsede']

    # send the NPI
    amie.send_packet(npi)

    log.info("Notification sent to ACCESS database")


if __name__ == "__main__":
    raise SystemExit(main())
