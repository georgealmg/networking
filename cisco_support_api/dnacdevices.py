#!/usr/bin/env python3

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from tqdm import tqdm
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        
DNACdata = []

def dnac_devices(dnac,headers,DNACdata):
    url = f"https://{dnac}/dna/intent/api/v1/network-device?limit=500"
    response = requests.request("GET", url, headers=headers, verify=False)
    for entry in response.json()["response"]:
        serials = entry["serialNumber"].split(",")
        models = entry["platformId"].split(",")
        for id in range(0,len(serials)):
            hostname = entry["hostname"]
            model = models[id].lstrip(" ")
            serial = serials[id].lstrip(" ")
            os = entry["softwareType"]
            version = entry["softwareVersion"]
            DNACdata.append({"Hostname":hostname,"ProductID":model,"SerialNumber":serial,"OS":os,"OSVersion":version})

def dnacdata(env_vars,DNACdata):

    user = env_vars["user"]
    pas = env_vars["sdn_pass"]
    dnac = env_vars["dnac"]
    headers = {"Content-Type":"application/json", "Accept":"application/json"}
    url = f"https://{dnac}/dna/system/api/v1/auth/token"
    response = requests.request("POST", url, headers=headers, auth=(user,pas), verify=False)
    token = response.json()["Token"]
    headers["X-Auth-Token"] = token
    with tqdm(total=1,desc="Extracting DNAC devices data") as pbar:
        dnac_devices(dnac,headers,DNACdata)
        pbar.update(1)