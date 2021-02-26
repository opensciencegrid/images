#!/usr/bin/env python
# -*- coding: utf-8 -*-

# https://developer.statuspage.io/#operation/postPagesPageIdSubscribers

import requests
from requests.structures import CaseInsensitiveDict
import json


class StatusApi():

    page_id = ''
    base_url = ''
    api_key = ''
    headers = CaseInsensitiveDict()

    def __init__(self, page_id, api_key):
        self.page_id = page_id
        self.base_url = 'https://api.statuspage.io/v1/pages/' + self.page_id
        self.api_key = api_key
        self.headers['Content-Type'] = 'application/json'
        self.headers['Authorization'] = 'OAuth ' + self.api_key
        
    def new_subscriber(self, 
                 email = '',
                 endpoint = None,
                 phone_country = '',
                 phone_number = '',
                 skip_confirmation_notification = True,
                 page_access_user = ''):
        subscriber = {
            'subscriber': {
                'email': email,
                'endpoint': endpoint,
                'phone_country': phone_country,
                'phone_number': phone_number,
                'skip_confirmation_notification': skip_confirmation_notification,
                'page_access_user': page_access_user,
                #'component_ids':  compunent_ids 
                }
            }
        return (subscriber)

    def create_a_subscriber(self, subscriber):
        url = self.base_url + '/subscribers'
        print(subscriber)
        resp = requests.post(url, headers=self.headers, json=subscriber)
        print(resp.status_code)
        if resp.status_code == 201:
            print('subscribed successfully')
            return(0)
        else:
            try:
                print('Status Code: %s' % resp.status_code)
                print(resp.content.decode())
            except:
                print('Unknown Error!')
                print('Could not subscribe %s' % subscriber)
            return(1)

    def subscribe_a_list(self, subscriber_list):
        for subscriber in subscriber_list:
            self.create_a_subscriber(subscriber)
        
    def get_subscribers(self, is_subscribed = True):
        '''
        If is_subscribed == True, return subscribed subscribers,
        Otherwise return unsubscribed subscribers.
        subscribe_type is one of 'email', 'sms', 'webhook', 'slack', 'integration_partner'
        '''
        if is_subscribed == True:
            #print('These are current subscribers:')
            url = self.base_url + '/subscribers'  
        else:
            #get unsubscribed subscribers
            #print('These subscribers unsubscribed from the status page:')
            url = self.base_url + '/subscribers/unsubscribed'   
        resp = requests.get(url, headers=self.headers)
        #print(resp.status_code)
        if resp.status_code == 200:
            j_obj = json.loads(resp.content)
            #print(j_obj)      
        else:
            try:
                print(resp.content.decode())
                print('Status Code:' + resp.status_code)
            except:
                print('Unknown Error!')
        return(j_obj)
    
    def unsubscribe_a_subscriber(self, subscriber_id):
        '''
        Unsubscribe a subscriber by id
        '''
        url = self.base_url + '/subscribers/' + str(subscriber_id)
        resp = requests.delete(url, headers=self.headers)
        j_obj = None
        if resp.status_code == 200:
            j_obj = json.loads(resp.content)
            #print(j_obj)      
        else:
            try:
                print(resp.content.decode())
                print('Status Code:' + resp.status_code)
            except:
                print('Unknown Error!')
        return(j_obj)