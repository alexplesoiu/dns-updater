"""
DNS Updater
Author: Alexandru-Ioan Plesoiu
GitHub: https://github.com/alexplesoiu
Documentation: https://github.com/alexplesoiu/dns-updater

DNS Updater is a Python-based tool that automatically updates Cloudflare DNS records
with your public IP address. If your server's IP address changes frequently or you
have a dynamic IP, this tool ensures that your domains and subdomains always point
to the correct server. It can handle multiple domains and subdomains from multiple
zones, with proxying enabled or disabled. The tool runs checks and updates every
5 minutes and includes redundancy for IP checking services.
"""

import requests
import schedule
import time
import socket
import logging
import sys

# Replace with your actual data
API_KEY = 'your_cloudflare_api_key'
EMAIL = 'your_email'

# Define API endpoints
BASE_URL = 'https://api.cloudflare.com/client/v4/'

# List of IP checking services
IP_CHECK_SERVICES = [
    'https://adresameaip.ro/ip',
    'https://api.ipify.org',
    'https://icanhazip.com',
    'https://ipinfo.io/ip'
]

# List of zones and domains to update
DOMAINS_TO_UPDATE = [
    {
        'zone_id': 'zone_id_1',
        'domain': 'subdomain1.mgedev.com',
        'proxied': True
    },
    {
        'zone_id': 'zone_id_1',
        'domain': 'subdomain2.mgedev.com',
        'proxied': False
    },
    {
        'zone_id': 'zone_id_2',
        'domain': 'subdomain1.mgesoftware.com',
        'proxied': True
    }
]


def create_logger(level=logging.INFO):
    """ Create the logger object """
    logger = logging.getLogger("MGE-Logs")

    # Create handlers
    console_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler('dns_updater.log')

    console_handler.setLevel(level)
    file_handler.setLevel(logging.WARNING)

    # Create formatters and add it to handlers
    logger_format = logging.Formatter('%(asctime)s | %(filename)s | %(levelname)s | %(message)s')
    file_format = logging.Formatter('%(asctime)s | %(filename)s(%(lineno)d) | %(levelname)s | %(message)s')


    file_handler.setFormatter(file_format)
    console_handler.setFormatter(logger_format)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.setLevel(level)

    return logger

LOGGER = create_logger()


# Get current DNS record for the specified domain
def get_dns_record(zone_id, domain_name):
    headers = {
        'X-Auth-Email': EMAIL,
        'X-Auth-Key': API_KEY,
        'Content-Type': 'application/json',
    }

    params = {
        'name': domain_name,
    }

    response = requests.get(f'{BASE_URL}zones/{zone_id}/dns_records', headers=headers, params=params)

    if response.status_code == 200:
        records = response.json()['result']
        if records:
            return records[0]
    return None


# Update the DNS record
def update_dns_record(record_id, zone_id, name, record_type, content, ttl=120, proxied=True):
    headers = {
        'X-Auth-Email': EMAIL,
        'X-Auth-Key': API_KEY,
        'Content-Type': 'application/json',
    }

    data = {
        'type': record_type,
        'name': name,
        'content': content,
        'ttl': ttl,
        'proxied': proxied,
    }

    response = requests.put(f'{BASE_URL}zones/{zone_id}/dns_records/{record_id}', json=data, headers=headers)

    if response.status_code == 200:
        LOGGER.info(f"DNS record updated successfully: {name} ({record_type}) -> {content}")
    else:
        LOGGER.error(f"Failed to update DNS record: {response.json()}")


# Get public IP address from the list of IP checking services
def get_public_ip():
    for service in IP_CHECK_SERVICES:
        try:
            response = requests.get(service, timeout=5)
            if response.status_code == 200:
                return response.text.strip()
        except requests.exceptions.RequestException:
            continue
    return None


# Check if there is an active internet connection
def is_connected():
    try:
        host = socket.gethostbyname("www.cloudflare.com")
        socket.create_connection((host, 80), 2)
        return True
    except Exception:
        pass
    return False


# Function to run the check and update process
def check_and_update_dns():
    if not is_connected():
        LOGGER.error("No internet connection. Skipping check and update.")
        return

    public_ip = get_public_ip()

    if public_ip:
        for domain_data in DOMAINS_TO_UPDATE:
            zone_id = domain_data['zone_id']
            domain_name = domain_data['domain']
            proxied = domain_data['proxied']

            record = get_dns_record(zone_id, domain_name)

            if record:
                if public_ip != record['content']:
                    update_dns_record(
                        record['id'],
                        record['zone_id'],
                        domain_name,
                        record['type'],
                        public_ip,
                        proxied=proxied
                    )
                else:
                    LOGGER.info(f"IP addresses are the same for {domain_name}. No update needed.")
            else:
                # TODO: Add more logs, this error could also appear if the API Login fails
                LOGGER.error(f"DNS record for {domain_name} not found.")
    else:
        LOGGER.error("Failed to retrieve public IP. Skipping check and update.")


# Schedule the check and update process to run every 5 minutes
schedule.every(5).minutes.do(check_and_update_dns).run()

# Main loop
while True:
    schedule.run_pending()
    time.sleep(1)
