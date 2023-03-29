# DNS Updater

DNS Updater is a Python-based tool that automatically updates Cloudflare DNS records with your public IP address. If your server's IP address changes frequently or you have dynamic ip, this tool ensures that your domains and subdomains always point to the correct server. It can handle multiple domains and subdomains from multiple zones, with proxying enabled or disabled. The tool runs checks and updates every 5 minutes and includes redundancy for IP checking services.

## Features

- Update multiple domains/subdomains from different zones
- Enable or disable proxying for each domain
- Redundancy for IP checking services
- Automatically runs checks and updates every 5 minutes
- Docker support for easy deployment

## Prerequisites

- Python 3.11
- Docker (optional)

## Installation

Clone the repository:

```
git clone https://github.com/alexplesoiu/dns-updater.git
cd dns-updater
```


Install the required Python packages:
```
pip install -r requirements.txt
```

## Configuration

Edit the `update_dns.py` script and replace the placeholders for `API_KEY`, `EMAIL`, and the `DOMAINS_TO_UPDATE` list with your actual data.

Example configuration:
```
API_KEY = 'your_cloudflare_api_key'
EMAIL = 'your_email'
DOMAINS_TO_UPDATE = [
    {
        'zone_id': 'zone_id_1',
        'domain': 'subdomain1.example.com',
        'proxied': True
    },
    {
        'zone_id': 'zone_id_1',
        'domain': 'subdomain2.example.com',
        'proxied': False
    },
    {
        'zone_id': 'zone_id_2',
        'domain': 'subdomain.example.org',
        'proxied': True
    }
]
```

## Usage
Run the script:

```
python update_dns.py
```

## Docker Deployment
Build the Docker container:

```
docker build -t dns-updater .
```

Run the Docker container:
```
docker run -d --name dns-updater --restart unless-stopped dns-updater
```

This will run the container in detached mode and ensure it starts automatically when the server restarts, unless you explicitly stop it.