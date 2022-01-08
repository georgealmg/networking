#!/usr/bin/env python3
#v1.0.0

import json, requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

dnsdict = {}
recordstoignore = []
user ,password = None, None

# Por medio de este script se obtienen todos los registros DNS estaticos por medio de la REST API del infoblox.
# La data se almacena en un JSON.

def dnsdata():

    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    url = "https://10.40.16.107/wapi/v2.11/record:a?creator=STATIC&_return_fields%2B=creator&_return_as_object=1&_paging=1&_max_results=10000000&view=Servidores"
    print("Extrayendo registros DNS estaticos")
    response = requests.request("GET", url, auth=(user, password), verify=False)
    for entry in response.json()["result"]:
        if entry["name"] not in recordstoignore:
            if entry["ipv4addr"] not in dnsdict.keys():
                dnsdict[entry["ipv4addr"]] = []
                dnsdict[entry["ipv4addr"]].append(entry["name"])
            elif entry["ipv4addr"] in dnsdict.keys():
                dnsdict[entry["ipv4addr"]].append(entry["name"])
        elif entry["name"] in recordstoignore:
            pass

    url = "https://10.40.16.107/wapi/v2.11/record:a?creator=DYNAMIC&_return_fields%2B=creator&_return_as_object=1&_paging=1&_max_results=10000000&view=Servidores"
    print("Extrayendo registros DNS dinamicos")
    response = requests.request("GET", url, auth=("infobloxbch", password), verify=False)
    for entry in response.json()["result"]:
        if entry["name"] not in recordstoignore:
            if entry["ipv4addr"] not in dnsdict.keys():
                dnsdict[entry["ipv4addr"]] = []
                dnsdict[entry["ipv4addr"]].append(entry["name"])
            elif entry["ipv4addr"] in dnsdict.keys():
                dnsdict[entry["ipv4addr"]].append(entry["name"])
        elif entry["name"] in recordstoignore:
            pass
        
    file = open("dns.json","w")
    data = json.dumps(dnsdict, indent=4)
    file.write(data)
    file.close()