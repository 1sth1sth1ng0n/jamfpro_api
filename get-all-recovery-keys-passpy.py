#!/usr/bin/env python3
# encoding: utf-8

import os
from jps_api_wrapper.pro import Pro
import passpy
from datetime import date, datetime

# Configuration Options
override = True
page_limit = int(os.environ.get("PAGE_LIMIT", 1000))
jps_url = os.environ["JPS_URL"]
client_id = os.environ["CLIENT_ID"]
client_secret = os.environ["CLIENT_SECRET"]
gpgid = os.environ.get("GPGID")
prk_store = os.environ.get("PASSWORD_STORE_DIR")

# Initialize pass store if not already established
store = passpy.Store(store_dir=prk_store)
if not os.path.exists(prk_store):
    store.init_store(gpgid)

def fetch_all_items(api_method, **kwargs):
    """Manually handle pagination for the given API method."""
    all_items = []
    page = 0

    while True:
        response = api_method(page=page, page_size=page_limit, **kwargs)
        items = response.get('results', [])
        all_items.extend(items)

        if len(items) < page_limit:
            break

        page += 1

    return all_items

def fetch_and_store_recovery_keys():
    """Fetch recovery keys and serial numbers, then securely store matched pairs."""
    start_time = datetime.now()

    with Pro(jps_url, client_id, client_secret, client=True) as pro:
        # Fetch all recovery keys and associated Jamf computer IDs
        recovery_keys_data = fetch_all_items(pro.get_computer_inventory_filevaults)
        recovery_keys = {
            item['computerId']: item['personalRecoveryKey']
            for item in recovery_keys_data
        }

        # Fetch all serial numbers and associated Jamf computer IDs
        serial_numbers_data = fetch_all_items(pro.get_computer_inventories, section="HARDWARE")
        serial_numbers = {
            item['id']: item['hardware']['serialNumber']
            for item in serial_numbers_data
        }

        # Match recovery keys with serial numbers and store them
        prk_count = 0
        for jamf_id, recovery_key in recovery_keys.items():
            serial_number = serial_numbers.get(jamf_id)
            if serial_number and recovery_key:
                # Store encrypted recovery key with date-stamped directory tree
                key_path = f"{date.today()}/{serial_number}"
                store.set_key(key_path, recovery_key, force=override)
                prk_count += 1

        print(f"Recovery key(s) found and stored: {prk_count}")

    duration = datetime.now() - start_time
    print(f"Duration: {duration.total_seconds():.2f} seconds.")

def main():
    fetch_and_store_recovery_keys()

if __name__ == "__main__":
    main()