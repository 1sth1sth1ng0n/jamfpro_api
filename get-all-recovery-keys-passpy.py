#!/usr/bin/env python3
# encoding: utf-8
#
# ollyr - 20230116
#
#
'''USAGE: creates or modifies a local macos filevault prk 
(personal recovery key) store git repo using gnupg encryption keys.'''

'''NOTES: the jamf api filvevault endpoint does not include serial 
numbers in the response payload, only jamf ids. we need to iterate 
each jamf id to get a matching serial number.'''

import requests
import json
import os
import passpy
import gnupg
from datetime import date
from pathlib import Path

home = str(Path.home())
today = date.today()

'''OPTIONS:'''
# override existing prk value in key store
override = True
# limit prks to return (paging limit ~2000, jamf version 10.43.1-t1674743888)
page_size = 10

# set env variables
jamf_hostname = os.environ.get("JAMF_API_ENDPOINT")
user = os.environ.get("JAMF_API_USER_1")
pd = os.environ.get("JAMF_API_USER_1_PW")
gpgid = os.environ.get("GPGID")

prk_store = f'{home}/.prk-store'
gpg_bin='/opt/homebrew/bin/gpg'

'''define absolute path for gpg bin and store directory'''
store = passpy.Store(gpg_bin=gpg_bin, store_dir=prk_store)

'''create pass store if not already established'''
if not os.path.exists(prk_store):

    store.init_store(gpgid)
    store.init_git()

def get_token():

    token_url = f'{jamf_hostname}/api/v1/auth/token'
    headers = {'Accept': 'application/json', }
    response = requests.post(url=token_url, headers=headers, auth=(user, pd))
    response_json = response.json()
    print(f'...api token obtained from {jamf_hostname}')
    return response_json['token']


def drop_token(api_token):

    token_drop_url = f'{jamf_hostname}/api/v1/auth/invalidate-token'
    headers = {'Accept': '*/*', 'Authorization': 'Bearer ' + api_token}
    response = requests.post(url=token_drop_url, headers=headers)

    if response.status_code == 204:
        print('...api token invalidated.')
    else:
        print('...error invalidating api token.')

def get_device_attributes():

    count = 0
    api_token = get_token()
    headers = {'Accept': 'application/json', 'Authorization': 'Bearer ' + api_token}
    all_recoverys_keys = f'{jamf_hostname}/api/v1/computers-inventory/filevault?page=0&page-size={page_size}'
    rk_response = requests.get(all_recoverys_keys, headers=headers)

    if rk_response.status_code == 200:
        '''create dict from json response'''
        data = json.loads(rk_response.content.decode('utf-8'))

        '''loop response and lookup serial numbers individually'''
        for item in data['results']:
            jamf_id = item['computerId']
            recovery_key = item['personalRecoveryKey']
            serial_number_endpoint = f'{jamf_hostname}/api/v1/computers-inventory/{jamf_id}?section=HARDWARE'
            sn_response = requests.get(serial_number_endpoint, headers=headers)
    
            if sn_response.status_code == 200:
                count += 1
                '''create dict from json response'''
                sn_data = json.loads(sn_response.content.decode('utf-8'))
                serial_number = sn_data['hardware']['serialNumber']

                '''store encrypted recovery keys in pass store with device sn and day-stamped directory tree'''
                store.set_key(str(today)+"/"+serial_number, recovery_key,force=override)

            else:
                print('...error:', sn_response.content.decode('utf-8'))
            
    else:
        print('...error:', rk_response.content.decode('utf-8'))

    print(f'recovery key(s) found = {count}')

    drop_token(api_token)


def main():
    
    get_device_attributes()
    
if __name__ == '__main__':
    main()