# !/usr/bin/env python3

import concurrent.futures, json, requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from tqdm import tqdm
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

apics,ACIdata = [],[]

def apic_cookie(apic,headers,payload):
    url = f"https://{apic}/api/aaaLogin.json"
    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    if response.status_code == 401:
        raise(requests.HTTPError(response.text))
    elif response.status_code == 200:
        token = response.json()["imdata"][0]["aaaLogin"]["attributes"]["token"]
        headers["Cookie"] = "APIC-cookie="+token
    elif response.status_code != 200:
        raise(requests.HTTPError(response.text))

def apic_pods(pods,response):
    response = response.json()
    for entry in response["imdata"]:
        id = entry["fabricPod"]["attributes"]["id"]
        pods.append(id)

def apic_devices(apic,headers,payload,ACIdata):
    pods = []
    url = f"https://{apic}/api/node/class/fabricPod.json"
    response = requests.request("GET", url, headers=headers, verify=False)
    if response.status_code == 403:
        apic_cookie(apic,headers,payload)
        response = requests.request("GET", url, headers=headers, verify=False)
    response.raise_for_status()
    apic_pods(pods,response)
    for pod in pods:
        url = f"https://{apic}/api/node/mo/topology/pod-{pod}.json?query-target=children&target-subtree-class=fabricNode"
        response = requests.request("GET", url, headers=headers, verify=False)
        if response.status_code == 403:
            apic_cookie(apic,headers,payload)
            response = requests.request("GET", url, headers=headers, verify=False)
        response.raise_for_status()
        response = response.json()
        for entry in response["imdata"]:
            hostname = entry["fabricNode"]["attributes"]["name"]
            model = entry["fabricNode"]["attributes"]["model"]
            serial = entry["fabricNode"]["attributes"]["serial"]
            os = "aci"
            version = entry["fabricNode"]["attributes"]["version"].strip("n9000-")
            ACIdata.append({"Hostname":hostname,"ProductID":model,"SerialNumber":serial,"OS":os,"OSVersion":version})
    pods.clear()

def acidata(env_vars,apics,ACIdata):

    user = env_vars["user"]
    pas = env_vars["sdn_pass"]
    apic1 = env_vars["apic1"]
    apics = [apic1]
    payload = json.dumps({"aaaUser": 
    {"attributes": 
    {"name":user,"pwd":pas}
    }
    })
    headers = {"Content-Type":"application/json"}
    with tqdm(total=len(apics),desc="Extracting APIC devices data") as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            ejecucion = {executor.submit(apic_devices,apic,headers,payload,ACIdata): apic for apic in apics}
        for output in concurrent.futures.as_completed(ejecucion):
            output.result()
            pbar.update(1)