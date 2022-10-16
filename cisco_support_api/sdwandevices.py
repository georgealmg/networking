#!/usr/bin/env python3

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from tqdm import tqdm
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

SDWdata = []
headers = {'Content-Type': 'application/x-www-form-urlencoded'}

def sdw_devices(vmanage,headers,SDWdata):
    url = f"https://{vmanage}/dataservice/device"
    response = requests.request("GET", url, headers=headers, verify=False)
    for entry in response.json()["data"]:
        if entry["device-type"] == "vedge":
            hostname = entry["host-name"]
            uuid = entry["uuid"]
            if "/" in uuid:
                model_serial = uuid.split("-")
                model = model_serial[0]
                serial = model_serial[1]
            elif "/" not in uuid:
                model_serial = uuid.split("-")
                model = model_serial[0]+"-"+model_serial[1]
                serial = model_serial[2]
            os = "iosxe"
            version = entry["version"].split(".")
            if version[1] != "0":
                version[1] = version[1].lstrip("0")
            if version[2] != "0":
                version[2] = version[2].lstrip("0")
            version = version[0]+"."+version[1]+"."+version[2]
            SDWdata.append({"Hostname":hostname,"ProductID":model,"SerialNumber":serial,"OS":os,"OSVersion":version})

def sdwdata(env_vars,SDWdata):

    user = env_vars["user"]
    pas = env_vars["sdn_pass"]
    vmanage = env_vars["vmanage"]
    url = f"https://{vmanage}/j_security_check"
    payload = f"j_username={user}&j_password={pas}"
    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    headers["Cookie"] = response.headers["set-cookie"].split(";")[0]
    with tqdm(total=1,desc="Extracting SDWAN devices data") as pbar:
        sdw_devices(vmanage,headers,SDWdata)
        pbar.update(1)