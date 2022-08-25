#!/usr/bin/env python3
#v1.0.0

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from tqdm import tqdm

dnsdict = {}
recordstoignore = []

# This script will retrieve all dynamic & static A records configured in the Infoblox server.
def dnsdata(dnsuser,dnspas,recordstoignore,dnsdict):

    with tqdm(total=2,desc="DNSdata") as pbar:
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        url = "https://infobloxip/wapi/v2.12/record:a?creator=STATIC&_return_fields%2B=creator&_return_as_object=1&_paging=1&_max_results=10000000&view=default"
        response = requests.request("GET", url, auth=(dnsuser, dnspas), verify=False)
        for entry in response.json()["result"]:
            if entry["name"] not in recordstoignore:
                if entry["ipv4addr"] not in dnsdict.keys():
                    dnsdict[entry["ipv4addr"]] = []
                    dnsdict[entry["ipv4addr"]].append(entry["name"])
                elif entry["ipv4addr"] in dnsdict.keys():
                    dnsdict[entry["ipv4addr"]].append(entry["name"])
            elif entry["name"] in recordstoignore:
                pass
        pbar.update(1)

        url = "https://infobloxip/wapi/v2.12/record:a?creator=DYNAMIC&_return_fields%2B=creator&_return_as_object=1&_paging=1&_max_results=10000000&view=default"
        response = requests.request("GET", url, auth=(dnsuser, dnspas), verify=False)
        for entry in response.json()["result"]:
            if entry["name"] not in recordstoignore:
                if entry["ipv4addr"] not in dnsdict.keys():
                    dnsdict[entry["ipv4addr"]] = []
                    dnsdict[entry["ipv4addr"]].append(entry["name"])
                elif entry["ipv4addr"] in dnsdict.keys():
                    dnsdict[entry["ipv4addr"]].append(entry["name"])
            elif entry["name"] in recordstoignore:
                pass
        pbar.update(1)