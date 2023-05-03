#!/usr/bin/python3

import configparser
import hashlib
import json
import os
import re
import requests

from pprint import pprint

CONNECT_URL = 'https://api.ci-connect.net:18080/v1alpha1'

MAILCHIMP_URL = 'https://us3.api.mailchimp.com/3.0'

COMANAGE_URL = 'https://registry.cilogon.org/registry'

# global config 
config = None
tag_id_cache = {}


def connect_url(path):
    return CONNECT_URL + path + '?token=' + config.get('osgconnect', 'token')


def mc_url(path):
    return MAILCHIMP_URL + path 


def connect_find_users(users):
    resp = requests.get(connect_url('/users'))
    if resp.status_code != 200:
        raise ApiError('Cannot fetch users: {}'.format(resp.status_code))
    for item in resp.json()['items']:

        if 'metadata' not in item:
            continue

        connect = item['metadata']

        # skip service accounts and so on
        if connect['service_account'] == True:
            continue
        if 'email' not in connect:
            continue

        # lowercase emails so we can compare later
        connect['email'] = str.lower(connect['email'])

        mydata = {}
        if connect['email'] in users:
            mydata = users[connect['email']]
        else:
            users[connect['email']] = mydata
        connect['connect_unix_name'] = connect['unix_name']

        for piece in ['email', 'name', 'connect_unix_name']:
            if piece not in mydata or \
               mydata[piece] != connect[piece]:
                mydata[piece] = connect[piece]
    
        if not 'tags' in mydata:
            mydata['tags'] = []

        # split name into first and last name
        mydata['firstname'] = str.strip(re.sub(' .*', '',  mydata['name']))
        mydata['lastname'] = str.strip(mydata['name'][len(mydata['firstname']) + 1:])
    

def connect_apply_tag(users, tag, group):
    '''
    Tags a group of users with the given tag
    '''

    tag_id = mc_get_tag_id(tag)

    resp = requests.get(connect_url('/groups/' + group + '/members'))
    if resp.status_code != 200:
        raise ApiError('Cannot fetch users: {}'.format(resp.status_code))
    for item in resp.json()['memberships']:
        # is there a better way to do this?
        for email, data in users.items():
            if 'connect_unix_name' in data and \
               data['connect_unix_name'] == item['user_name']:
                if item['state'] in ['active', 'admin']:
                    if tag not in data['tags']:
                        data['tags'].append(tag)
                break


def comanage_mkrequest(method, target, data=None, **kw):
    resp = None
    url = os.path.join(COMANAGE_URL, target)
    if kw:
        url += "?" + "&".join( "{}={}".format(k.replace('__', '.'),v) for k,v in kw.items() )
    if method == 'GET':
        resp = requests.get(url, auth=(config.get('comanage', 'api_username'), config.get('comanage', 'api_password')))
    return resp


def comanage_find_users(users):

    co_users = {}

    # we have to do 3 calls to get co persons, emails and names
    resp = comanage_mkrequest('GET', 'co_people.json', coid=7)
    if resp.status_code != 200:
        raise ApiError('Cannot fetch users: {}'.format(resp.status_code))
    for u in resp.json()['CoPeople']:
        if u['Status'] == 'Active' and u['Deleted'] == False:
            co_users[u['Id']] = {'co_person_id': u['Id'], 'tags': []}

    # add emails
    resp = comanage_mkrequest('GET', 'email_addresses.json', coid=7)
    if resp.status_code != 200:
        raise ApiError('Cannot fetch emails: {}'.format(resp.status_code))
    for e in resp.json()['EmailAddresses']:
        pid = e['Person']['Id']
        if pid in co_users:
            co_users[pid]['email'] = str.lower(e['Mail'])
    
    # add names
    resp = comanage_mkrequest('GET', 'names.json', coid=7)
    if resp.status_code != 200:
        raise ApiError('Cannot fetch names: {}'.format(resp.status_code))
    for n in resp.json()['Names']:
        if n.get('PrimaryName', False) == True:
            pid = n['Person']['Id']
            if pid in co_users:
                co_users[pid]['firstname'] = n['Given']
                co_users[pid]['lastname'] = n['Family']

    # now add the users the main list, indexed by email
    for pid, u in co_users.items():
        if u['email'] not in users:
            users[u['email']] = u
        else:
            # update user 
            for attr in ['co_person_id', 'firstname', 'lastname', 'email']:
                users[u['email']][attr] = u[attr]


def comanage_apply_tag(users, tag, co_group_name):

    # find the group id
    resp = comanage_mkrequest('GET', 'co_groups.json', coid=7, search__identifier=co_group_name)
    if resp.status_code != 200:
        raise ApiError('Cannot fetch groups: {}'.format(resp.status_code))
    if len(resp.json()['CoGroups']) != 1:
        raise ApiError('Wrong number of groups: {}'.format(resp.json()['CoGroups']))
    gid = resp.json()['CoGroups'][0]['Id']

    # find all members
    member_pids = []
    resp = comanage_mkrequest('GET', 'co_group_members.json', coid=7, cogroupid=gid)
    if resp.status_code != 200:
        raise ApiError('Cannot fetch members: {}'.format(resp.status_code))
    for item in resp.json()['CoGroupMembers']:
        member_pids.append(item['Person']['Id'])

    # check all users, and tag as needed
    for email, u in users.items():
        if 'co_person_id' not in u:
            continue
        if u['co_person_id'] in member_pids:
            if tag not in u['tags']:
                u['tags'].append(tag)


def mc_get_tag_id(name):
    '''
    Query/create tags
    '''
    global tag_id_cache

    if name in tag_id_cache:
        return tag_id_cache[name]

    # find the mailchimp id
    resp = requests.get(mc_url('/lists/21a88cec7e/segments?count=100'),
                        auth=('anystring', config.get('mailchimp', 'token')))
    if resp.status_code != 200:
        raise ApiError('Cannot fetch tags: {}'.format(resp.status_code))
    for item in resp.json()['segments']:
        if item['name'] == name:
            tag_id_cache[name] = item['id']
            return item['id']

    # not found create
    data = {
        'name': name,
        'static_segment': []
    }
    resp = requests.post(mc_url('/lists/21a88cec7e/segments'),
                         json=data,
                         auth=('anystring', config.get('mailchimp', 'token')))
    if resp.status_code != 200:
        raise RuntimeError('Unable to create tag: {} {} {}'.format(name, resp.status_code, resp.content))

    # find the new id
    resp = requests.get(mc_url('/lists/21a88cec7e/segments?count=100'),
                        auth=('anystring', config.get('mailchimp', 'token')))
    if resp.status_code != 200:
        raise ApiError('Cannot fetch tags: {}'.format(resp.status_code))
    for item in resp.json()['segments']:
        if item['name'] == name:
            tag_id_cache[name] = item['id']
            return item['id']

    # still not found - error
    raise RuntimeError('Unable to determine the tag id for tag ' + name)


def mc_update(data):
    # first try to update, and if that does not work, create the record

    package = {
            'email_address': data['email'],
            'merge_fields': {
                'FNAME': data['firstname'],
                'LNAME': data['lastname']
                }
            }

    # try update
    resp = requests.patch(mc_url('/lists/21a88cec7e/members/' + data['mc_hash']),
                          json=package,
                          auth=('anystring', config.get('mailchimp', 'token')))
    if resp.status_code != 200:

        # try create
        package['status'] = 'subscribed'
        resp = requests.post(mc_url('/lists/21a88cec7e/members/'),
                             json=package,
                             auth=('anystring', config.get('mailchimp', 'token')))
        if resp.status_code != 200:
            print('  Cannot update user: {}'.format(resp.status_code))
            return


    # update tags 
    package = { "email_address": data['email']}
    for tag in data['tags']:
        tag_id = mc_get_tag_id(tag)
        resp = requests.post(mc_url('/lists/21a88cec7e/segments/' + str(tag_id) + '/members'),
                                    json=package,
                                    auth=('anystring', config.get('mailchimp', 'token')))
        if resp.status_code != 200:
            print('  Cannot update tag for user: {}'.format(resp.status_code))

                    
def load_state():
    users = {}
    try:
        with open('data/state.json') as f:
            users = json.loads(f.read())
    except:
        pass
    return users


def write_state(users):
    with open('data/state.json', 'w') as f:
        f.write(json.dumps(users, indent=2))


def main():
    global config

    config = configparser.ConfigParser()
    config.read_file(open('mailchimp-sync.conf'))

    users = load_state()

    # osgconnect users
    connect_find_users(users)
    connect_apply_tag(users, 'ATLAS',       'root.atlas')
    connect_apply_tag(users, 'CMS',         'root.cms')
    connect_apply_tag(users, 'Duke',        'root.duke')
    connect_apply_tag(users, 'OSG-Connect', 'root.osg')
    connect_apply_tag(users, 'SPT',         'root.spt')
    connect_apply_tag(users, 'UChicago',    'root.uchicago')
    connect_apply_tag(users, 'XENONnT',     'root.xenon1t')
    connect_apply_tag(users, 'Snowmass21',  'root.snowmass21')
    # OSPool is a meta tag spanning our sites
    connect_apply_tag(users, 'OSPool', 'root.osg')

    # comanage
    comanage_find_users(users)
    comanage_apply_tag(users, 'PATh-Facility', 'ap1-login')
    comanage_apply_tag(users, 'OSPool-Wisc', 'ap7-login')
    # OSPool is a meta tag spanning our sites
    comanage_apply_tag(users, 'OSPool', 'ap7-login')

    # update mailchimp
    for email, data in users.items():
        # determine if we the user needs updating - do this
        # to save on the MailChimp API calls
        dirty = False

        # skip in no tags
        if 'tags' not in data or \
           len(data['tags']) == 0:
            continue

        # mailchimp uses the mail, lowercase, md5 as id
        data['mc_hash'] = hashlib.md5(str.lower(data['email']).encode('utf-8')).hexdigest()

        if 'prev_tags' not in data or \
           set(data['tags']) != set(data['prev_tags']):
            dirty = True

        if dirty:
            print('')
            pprint(data)
            print('Updating: {}'.format(email))
            mc_update(data)

    # keep track of last state of tags, so we know what to update next time
    for email, u in users.items():
        u['prev_tags'] = u['tags']

    write_state(users)

main()

