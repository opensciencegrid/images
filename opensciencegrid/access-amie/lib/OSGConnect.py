#!/usr/bin/python3

import configparser
import json
import logging
import requests

log = logging.getLogger('accessamie')


# This class is mostly used with data from the ACCESS AMIE system, and thus
# there is a built in flexibility here to deal with the fact that sometimes
# we get local username, and some time local uid, from AMIE. When a "user"
# is specified in this interface, it can be either username or uid, and it
# will be interpreted based on if is numeric (uid), or alphanumeric.
# (username). If we have a uid, it will be quickly mapped to a username.

class OSGConnect():
    config = None
    base_url = None
    token = None

    def __init__(self, config):
        self.config = config
        self.base_url = config.get('connect', 'url')
        self.token = config.get('connect', 'token')

    # def update_user(self, username, ...):

    def _get(self, path):
        if path[0] != '/':
            path = '/{}'.format(path)
        resp = requests.get('{}{}?token={}'.format(self.base_url, path, self.token))
        if resp.status_code != 200:
            raise RuntimeError('Error {} from: {}{}'.format(resp.status_code, self.base_url, path))
        return resp.json()

    def _post(self, path, data):
        if path[0] != '/':
            path = '/{}'.format(path)
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        resp = requests.post('{}{}?token={}'.format(self.base_url, path, self.token), json=data, headers=headers)
        if resp.status_code != 200:
            raise RuntimeError('Error {} from: {}{}'.format(resp.status_code, self.base_url, path))
        return resp.json()

    def _put(self, path, data):
        if path[0] != '/':
            path = '/{}'.format(path)
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        resp = requests.put('{}{}?token={}'.format(self.base_url, path, self.token), json=data, headers=headers)
        if resp.status_code != 200:
            raise RuntimeError('Error {} from: {}{}'.format(resp.status_code, self.base_url, path))
        return resp.raw

    def _delete(self, path):
        if path[0] != '/':
            path = '/{}'.format(path)
        resp = requests.delete('{}{}?token={}'.format(self.base_url, path, self.token))
        if resp.status_code != 200:
            raise RuntimeError('Error {} from: {}{}'.format(resp.status_code, self.base_url, path))
        return resp.raw

    def _uid_to_username(self, uid):
        data = self._get('/users')
        for item in data['items']:
            if str(uid) == str(item['metadata']['unix_id']):
                return item['metadata']['unix_name']
        raise RuntimeError('User not found')

    def project(self, name):
        data = self._get('/groups/root.osg.{}'.format(name))
        if 'metadata' not in data:
            raise RuntimeError("Group does not exist in OSGConnect")
        return data['metadata']

    def user(self, id):
        # id can be uid or username
        if str(id).isdecimal():
            username = self._uid_to_username(id)
        else:
            username = id

        data = self._get('/users/{}'.format(username))
        if 'metadata' not in data:
            raise RuntimeError("User does not exist in OSGConnect")
        return data['metadata']

    def add_user_to_project(self, project, user):
        # look up the user
        username = self.user(user)['unix_name']
        data = {
            'group_membership': {
                'state': 'active'
            }
        }
        self._put('/groups/root.osg.{}/members/{}'.format(project, username), data)
        return True

    def remove_user_from_project(self, project, user):
        # look up the user
        username = self.user(user)['unix_name']
        self._delete('/users/{}/groups/root.osg.{}'.format(username, project))
        return True


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('/opt/access-amie/etc/access-amie.conf')
    connect = OSGConnect(config)
    assert connect._uid_to_username(42312) == 'rynge', 'UID 42312 is user rynge'
    assert connect.user('42312')['unix_name'] == 'rynge', 'User rynge found'
    assert connect.user('rynge')['unix_id'] == 42312, 'User rynge found'
    assert connect.project('OSG-Staff')['unix_id'] == 7158, 'GID 7158 is OSG-Staff'
    assert connect.remove_user_from_project('OSGUserTrainingPilot', 'rynge'), 'Removing user from project'
    assert connect.add_user_to_project('OSGUserTrainingPilot', 'rynge'), 'Adding user to project'
    print('All tests passed')
