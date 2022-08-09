#!/usr/bin/env python3
#v1.0.2

import concurrent.futures, json, os, requests
from getpass import getuser
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from tqdm import tqdm

apics = {"APIC1":{},"APC2":{}}
headers = {"Content-Type":"application/json"}
cookie,nodes = {},{}
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# This method is used to generate the cookie required for all API calls.
def apic_cookie(apic,headers,payload):
    url = f"https://{apic}/api/aaaLogin.json"
    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    if response.status_code == 401:
        raise(requests.HTTPError(response.text))
    elif response.status_code == 200:
        token = response.json()["imdata"][0]["aaaLogin"]["attributes"]["token"]
        cookie["Cookie"] = "APIC-cookie="+token
    elif response.status_code != 200:
        raise(requests.HTTPError(response.text))

# This method is used to get a list of pods configured in each ACI fabric.
def apic_pods(apic,response):
    response = response.json()
    apics[apic]["pods"] = {}
    for entry in response["imdata"]:
        id = entry["fabricPod"]["attributes"]["id"]
        apics[apic]["pods"][id] = ""

# This method is used to get a list of devices configured in each of the pods of the ACI fabric.
# Said list will be used to replace the node id with the node hostname.
def apic_devices(response):
    response = response.json()
    for entry in response["imdata"]:
        name = entry["fabricNode"]["attributes"]["name"]
        id = entry["fabricNode"]["attributes"]["id"]
        nodes[id] = name

# This method will call the other methods and will also get a list of all endpoints in the ACI fabric.
def aci_ep(apic,headers,payload,acidf):
    
    url = f"https://{apic}/api/node/class/fabricPod.json"
    response = requests.request("GET", url, headers=cookie, verify=False)
    if response.status_code == 403:
        apic_cookie(apic,headers,payload)
        response = requests.request("GET", url, headers=cookie, verify=False)
    response.raise_for_status()
    apic_pods(apic,response)
    for pod in apics[apic]["pods"].keys():
        url = f"https://{apic}/api/node/mo/topology/pod-{pod}.json?query-target=children&target-subtree-class=fabricNode"
        response = requests.request("GET", url, headers=cookie, verify=False)
        if response.status_code == 403:
            apic_cookie(apic,headers,payload)
            response = requests.request("GET", url, headers=cookie, verify=False)
        response.raise_for_status()
        apic_devices(response)

    response = requests.request("GET", url=f"https://{apic}/api/node/class/fvCEp.json?", 
    headers=cookie, verify=False, params={"rsp-subtree":"full","rsp-subtree-class":"fvCEp,fvRsCEpToPathEp"})
    if response.status_code == 403:
        apic_cookie(apic,headers,payload)
        response = requests.request("GET", url=f"https://{apic}/api/node/class/fvCEp.json?", 
        headers=cookie, verify=False, params={"rsp-subtree":"full","rsp-subtree-class":"fvCEp,fvRsCEpToPathEp"})
    response.raise_for_status()
    try:
        response = response.json()["imdata"]
        for entry in response:
            try:
                ip = entry["fvCEp"]["attributes"]["ip"]
                mac = entry["fvCEp"]["attributes"]["mac"]
                inter = entry["fvCEp"]["children"][0]["fvRsCEpToPathEp"]["attributes"]["tDn"]
                vlan = entry["fvCEp"]["attributes"]["encap"]
                acidf.append({"ip":ip,"mac":mac,"interface":inter,"vlan":vlan})
            except(KeyError,IndexError):
                pass
    except(KeyError,IndexError):
        pass

def acidata(user,pas,apics,headers,acidf):

    payload = json.dumps({"aaaUser": 
    {"attributes": 
    {"name":user ,"pwd": pas}
    }
    })

    with tqdm(total=len(apics),desc="ACIdata") as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            ejecucion = {executor.submit(aci_ep,apic,headers,payload,acidf): apic for apic in apics.keys()}
        for output in concurrent.futures.as_completed(ejecucion):
            output.result()
            pbar.update(1)