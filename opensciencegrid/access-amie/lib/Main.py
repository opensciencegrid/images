#!/usr/bin/python3

import configparser
import logging
import re
import time
import pprint
import uuid
from datetime import datetime, timedelta
from logging.config import dictConfig
from amieclient.usage import ComputeUsageRecord

from AMIE import AMIE
from AMIE_Usage import AMIE_Usage
from FreshDesk import FreshDesk
from GRACC import GRACC, GRACCState

log_config = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'default': {
            'format': '%(asctime)s [%(levelname)s] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',

        },
    },
    'handlers': {
        'default': {
            'formatter': 'default',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
        },
    },
    'loggers': {
        '': { # root logger
            'handlers': ['default'],
            'level': 'WARNING',
            'propagate': False
        },
        'accessamie': {
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

dictConfig(log_config)
log = logging.getLogger('accessamie')


class Main():
    config = None
    amie = None
    connect = None
    freshdesk = None

    def __init__(self):

        log.info('Reading config from /opt/access-amie/etc/access-amie.conf')
        self.config = configparser.ConfigParser()
        self.config.read('/opt/access-amie/etc/access-amie.conf')

        self.amie = AMIE(self.config)
        self.amie_usage = AMIE_Usage(self.config)
        self.freshdesk = FreshDesk(self.config)

    def request_project_create(self, packet):

        grant_number = packet.GrantNumber
        record_id = packet.RecordID
        project_id = packet.ProjectID  # site project_id (if known)
        request_type = packet.RequestType
        allocation_type = packet.AllocationType  # new, renewal, supplement, transfer, adjustment, advance, extension, ...
        start_date = packet.StartDate
        end_date = packet.EndDate
        amount = packet.ServiceUnitsAllocated
        abstract = packet.Abstract
        project_title = packet.ProjectTitle
        board_type = packet.BoardType
        pfos_num = packet.PfosNumber

        pi_person_id = packet.PiPersonID  # site person_id for the PI (if known)
        pi_first_name = packet.PiFirstName
        pi_middle_name = packet.PiMiddleName
        pi_last_name = packet.PiLastName
        pi_organization = packet.PiOrganization
        pi_department = packet.PiDepartment
        pi_email = packet.PiEmail
        pi_phone_number = packet.PiBusinessPhoneNumber
        pi_nsf_status_code = packet.NsfStatusCode

        subject = f'OSG/ACCESS - create PI account to activate your allocation TG-{grant_number}'
        body = f'''<p>Thank you for your interest in using OSPool resources via an ACCESS allocation.
When you are ready to use your OSPool allocation, you (the allocation PI) need an account
with the OSG Connect service.</p>

<br>
<p>
<b>If you already have an OSG Connect user profile:</b><br>
You can check by trying to ‘Log In’ via the osgconnect.net website using your institutional
identity. If you are able to view your user Profile and are ready to charge OSPool usage against
your ACCESS allocation, please send an email to support@osg-htc.org, to request that your
user account be associated with the appropriate allocation charge code (e.g. TG-{grant_number}).
</p>

<br>
<p>
<b>If you do not yet have an OSG Connect user profile:</b><br>
Please ‘Sign Up’ for an account at https://connect.osg-htc.org/signup using your institutional
identity, and copy the below into the Comments field before submitting your Sign Up request.
</p>

<br>
<p>
Project: TG-{grant_number}<br/>
Title: {project_title}<br/>
PI: {pi_first_name} {pi_last_name}<br/>
Organization: {pi_organization}<br/>
Email: {pi_email}<br/>
</p>

<br>
<p>
An OSG Research Computing Facilitator will follow up to meet with you and/or your group, to
activate accounts and provide personalized guidance on using the OSPool.
</p>

<br>
<p>
<b>Users on your allocation can follow either step, above, after the allocation has been
activated by a staff member.</b>
</p>

<br>
<p>
Thank you,<br>
OSG User Facilitation
</p>
'''
        self.freshdesk.send_email(pi_email, subject, body, tags=['access_project'])
        self.amie.save_packet(packet, 'incoming', 'parked')

    def data_project_create(self, packet):
        # the data_project_create(DPC) packet has two functions:
        # 1. to let the site know that the project and PI account have been setup in the XDCDB
        # 2. to provide any new DNs for the PI that were added after the RPC was sent
        # NOTE: a DPC does *not* have the resource. You have to get the resource from the RPC for the trans_rec_id

        person_id = packet.PersonID
        project_id = packet.ProjectID
        dn_list = packet.DnList

        # construct the InformTransactionComplete(ITC) success packet
        itc = packet.reply_packet()
        itc.StatusCode = 'Success'
        itc.DetailCode = '1'
        itc.Message = 'OK'

        # send the ITC
        self.amie.send_packet(itc)

    def request_account_create(self, packet):
        packet.pretty_print()
        grant_number = packet.GrantNumber
        project_id = packet.ProjectID  # site project_id
        resource = packet.ResourceList[0]  # xsede site resource name, eg, delta.ncsa.xsede.org

        user_global_id = packet.UserGlobalID
        user_person_id = packet.UserPersonID  # site person_id for the User (if known)
        user_first_name = packet.UserFirstName
        user_middle_name = packet.UserMiddleName
        user_last_name = packet.UserLastName
        user_organization = packet.UserOrganization
        user_department = packet.UserDepartment
        user_email = packet.UserEmail
        user_phone_number = packet.UserBusinessPhoneNumber
        user_phone_extension = packet.UserBusinessPhoneExtension
        user_address1 = packet.UserStreetAddress
        user_address2 = packet.UserStreetAddress2
        user_city = packet.UserCity
        user_state = packet.UserState
        user_zipcode = packet.UserZip
        user_country = packet.UserCountry
        user_requested_logins = packet.UserRequestedLoginList
        project_id = packet.ProjectID

        # RACs are also used to reactivate accounts, so if the account already exists, just set it active
        if user_person_id and len(user_person_id) > 1:
            try:
                user = self.connect.user(user_person_id)

                # ensure emails match
                if user_email == user['email']:
                    # construct a NotifyAccountCreate(NAC) packet.
                    nac = packet.reply_packet()
                    nac.UserRemoteSiteLogin = user['unix_name']  # local login for the User on the resource
                    nac.UserPersonID = user_person_id  # local person ID for the User
                    self.amie.send_packet(nac)
                    return
            except Exception:
                # unable to find/process the user - fall back to facilitators
                pass

        subject = f'OSG/ACCESS - create an account on OSG Connect'
        body = f'''<p>Thank you for your application for an OSG account via an ACCESS allocation. When you
are ready to use your allocation, you will need an account with the OSG Connect service.
</p>

<br>
<p>
<b>If you already have an OSG Connect user profile:</b><br>
You can double check by trying to ‘Log In’ via the https://connect.osg-htc.org/ website using your institutional identity.
If you are able to view your user Profile without needing to ‘Sign Up’ and are ready to charge OSPool usage
against your ACCESS allocation, please send an email to support@osg-htc.org, to request that your
user account be associated with the appropriate allocation charge code (e.g. {project_id}).
</p>

<br>
<p>
<b>If you do not yet have an OSG Connect user profile:</b><br>
Please ‘Sign Up’ for an account at https://connect.osg-htc.org/signup using your institutional identity, and
copy the below into the Comments field before submitting your ‘Sign Up’ request:
</p>

<br>
<p>
ACCESS Project: {project_id}<br/>
ACCESS global ID: {user_global_id}<br/>
</p>

<br>
<p>
An OSG Research Computing Facilitator will follow up to meet with you and/or your group, to activate
accounts and provide personalized guidance on using the OSPool.
</p>

<br>
<p>
Thank you,<br>
OSG User Facilitation
</p>
'''
        self.freshdesk.send_email(user_email, subject, body, tags=["access_account"])
        self.amie.save_packet(packet, 'incoming', 'parked')

    def data_account_create(self, packet):
        # the data_account_create(DAC) packet has two functions:
        # 1. to let the site know that the User account on the project has been setup in the XDCDB
        # 2. to provide any new DNs for the User that were added after the RAC was sent
        # NOTE: a DAC does *not* have the resource. You have to get the resource from the RAC for the trans_rec_id

        # As OSG is no longer doing any X.509, we will ignore the DN updates

        person_id = packet.PersonID
        project_id = packet.ProjectID
        dn_list = packet.DnList

        # construct the InformTransactionComplete(ITC) success packet
        itc = packet.reply_packet()
        itc.StatusCode = 'Success'
        itc.DetailCode = '1'
        itc.Message = 'OK'

        # send the ITC
        self.amie.send_packet(itc)

    def request_account_inactivate(self, packet):
        resource = packet.ResourceList[0]
        project_id = packet.ProjectID
        person_id = packet.PersonID

        log.info('Removing user {} from project {}'.format(person_id, project_id))
        # Disabled for initial switchover from xd-login
        # self.connect.remove_user_from_project(project_id, person_id)

        nai = packet.reply_packet()
        self.amie.send_packet(nai)

    def request_user_modify(self, packet):
        # person_id = packet.person_id
        # if packet.Actiontype == 'delete':
        #     # we are not using DNs anymore
        #     pass
        # else:
        #     first_name = packet.FirstName
        #     last_name = packet.LastName
        #     organization = packet.Organization
        #     department = packet.Department
        #     email = packet.Email
        #     bus_phone_number = packet.BusinessPhoneNumber
        #
        #     #self.connect.update_user(username, ....)

        # construct the InformTransactionComplete(ITC) success packet
        itc = packet.reply_packet()
        itc.StatusCode = 'Success'
        itc.DetailCode = '1'
        itc.Message = 'OK'

        # send the ITC
        self.amie.send_packet(itc)

    def request_person_merge(self, packet):
        raise RuntimeError('request_person_merge not implemented')

    def request_project_inactivate(self, packet):
        resource = packet.ResourceList[0]
        project_id = packet.ProjectID

        log.info('Deactivating {}'.format(project_id))
        try:
            self.connect.remove_all_users(project_id)
        except:
            # project might not exist
            pass

        nai = packet.reply_packet()
        self.amie.send_packet(nai)

    def request_project_reactivate(self, packet):
        resource = packet.ResourceList[0]
        project_id = packet.ProjectID
        pi_person_id = packet.PersonID

        log.info('Reactivating {}'.format(project_id))
        # self.connect.add_uid_to_project(project_id, pi_person_id)

        npr = packet.reply_packet()
        self.amie.send_packet(npr)

    def inform_transaction_complete(self, packet):
        # construct the InformTransactionComplete(ITC) success packet
        itc = packet.reply_packet()
        itc.StatusCode = 'Success'
        itc.DetailCode = '1'
        itc.Message = 'OK'

        # send the ITC
        self.amie.send_packet(itc)

    def main(self):

        while True:

            log.info('Starting new iteration...')

            # count parked packets
            packets = self.amie.load_packets('incoming', 'parked')
            log.info(' ... {} packets are parked and waiting for facilitators'.format(len(packets)))

            # now check the inbox
            packets = self.amie.list()

            if packets is not None:
                log.info(' ... {} packets in the inbox'.format(len(packets)))
                for packet in packets:
                    packet_type = packet.packet_type
                    packet_rec_id = packet.packet_rec_id
                    trans_rec_id = packet.trans_rec_id

                    if self.amie.already_processed(packet):
                        # skip packages we have already processed (or chosen to ignore)
                        continue

                    log.info("Handling new packet: type={} packet_rec_id={} trans_rec_id={}".format(
                        packet_type, packet_rec_id, trans_rec_id
                    ))

                    if packet_type == 'request_project_create':
                        self.request_project_create(packet)
                    elif packet_type == 'data_project_create':
                        self.data_project_create(packet)
                    elif packet_type == 'request_account_create':
                        self.request_account_create(packet)
                    elif packet_type == 'data_account_create':
                        self.data_account_create(packet)
                    elif packet_type == 'request_account_inactivate':
                        self.request_account_inactivate(packet)
                    elif packet_type == 'request_user_modify':
                        self.request_user_modify(packet)
                    elif packet_type == 'request_person_merge':
                        self.request_person_merge(packet)
                    elif packet_type == 'request_project_inactivate':
                        self.request_project_inactivate(packet)
                    elif packet_type == 'request_project_reactivate':
                        self.request_project_reactivate(packet)
                    elif packet_type == 'inform_transaction_complete':
                        self.inform_transaction_complete(packet)
                    else:
                        packet.pretty_print()
                        raise RuntimeError("We do not know how to handle packets of type {}".format(packet_type))

                    # always save a copy
                    self.amie.save_packet(packet, 'incoming', 'received')

            # send in usage information (pull from GRACC)
            q = GRACC(self.config)
            # loop over all the maps defined in the conf file
            for section in self.config.sections():
                if re.match("^graccusage_", section):
                    # we have a valid map
                    try:
                        state = GRACCState(self.config, section)
                        start_time = state.get_ts()
                    except Exception as e:
                        log.error(e)
                        log.error('Unable to query map {} - does it have a state file?'.format(section))
                        continue
                    data = q.query(section, start_time)
                    for item in data["data"]:
                        log.info(pprint.pformat(item))
                        local_record_id = str(uuid.uuid4())
                        charge = round(float(item['wall_duration']) / 3600.0, 2)
                        log.info('Assigned local record id {}, and charge {} SUs'.format(local_record_id, charge))
    
                        try:
                            # construct a ComputeUsageRecord packet
                            upack = ComputeUsageRecord(
                                resource = 'grid1.osg.xsede',
                                username = item['user'],
                                local_project_id = item['project_name'],
                                local_record_id = local_record_id,
                                charge = str(charge),
                                submit_time = item['start_time'],
                                start_time = item['start_time'],
                                end_time = item['end_time'],
                                node_count = item['nodes']
                            )
                            resp = self.amie_usage.send(upack)
                            for item in resp:
                                log.info(pprint.pformat(item.as_dict()))
                        except Exception as e:
                            log.error(e)
                            continue
                    # remember how far we have queried already
                    state.update_ts(data["max_date_str"])

            # check for usage record errors
            #try:
            #    log.info('Usage records status for the last 24 hours:')
            #    end_t = datetime.utcnow()
            #    start_t = end_t - timedelta(days=1)
            #    log.info(pprint.pformat(self.amie_usage.status(start_t, end_t)))
            #    # any errors?
            #    errors = self.amie_usage.get_failed_records()
            #    log.info(pprint.pformat(errors))
            #except Exception as e:
            #    log.error(e)

            # update the liveness file - k8s will use this to make sure we are still looping
            fname = self.config.get('main', 'state_dir') + '/liveness.state'
            with open(fname, "w") as fp:
                fp.write(str(datetime.utcnow()))                

            if self.config.getboolean('main', 'debug'):
                log.info('Debug mode: only sleeping 1 minute. For regular mode this is 1 hour.')
                log.info('---------------------------------------------------------------------------------------------------------------------------------')
                time.sleep(60)
            else:
                log.info('---------------------------------------------------------------------------------------------------------------------------------')
                time.sleep(3600)


if __name__ == '__main__':
    main = Main()
    main.main()
