#!/usr/bin/env python3
#v1.0.6

import concurrent.futures, requests
from ratelimit import RateLimitException, limits
from backoff import on_exception, expo
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from tqdm import tqdm
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

osdict,OSdata = {},[]

@on_exception(expo,RateLimitException,max_tries=5)
@limits(calls=10,period=1)
def apicall(os,headers,osdict,OSdata,pbar):
    for version in osdict[os]:
        url = f"https://api.cisco.com/security/advisories/{os}?version={version}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            psirt = response.json()
            if "errorCode" not in psirt.keys():
                psirt = response.json()["advisories"]
                for entry in psirt:
                    OSdata.append({"OSfamily":os,"OSversion":version,"BugID":str(entry["bugIDs"]),"advisoryTitle":entry["advisoryTitle"],"cves":str(entry["cves"])
                    ,"cwe":str(entry["cwe"]),"status":entry["status"],"firstPublished":entry["firstPublished"],
                    "lastUpdated":entry["lastUpdated"],"severity":entry["sir"],"firstFixed":str(entry["firstFixed"])
                    ,"url":entry["publicationUrl"]})
            elif "errorCode" in psirt.keys():
                    OSdata.append({"OSfamily":os,"OSversion":version,"BugID":"N/A","advisoryTitle":"N/A","cves":"N/A"
                    ,"cwe":"N/A","status":"N/A","firstPublished":"N/A",
                    "lastUpdated":"N/A","severity":"N/A","firstFixed":"N/A"
                    ,"url":"N/A"})
        elif response.status_code != 200:
            errorMessage = "HTTPError:"+str(response.status_code)
            OSdata.append({"OSfamily":os,"OSversion":version,"BugID":errorMessage,"advisoryTitle":errorMessage,"cves":errorMessage
            ,"cwe":errorMessage,"status":errorMessage,"firstPublished":errorMessage,
            "lastUpdated":errorMessage,"severity":errorMessage,"firstFixed":errorMessage
            ,"url":errorMessage})
    
        pbar.update(1)

def psirtdata(env_vars,devicesdf,osdict,OSdata):

    client_id = env_vars["client_id"]
    client_secret = env_vars["client_secret"]
    url = "https://cloudsso.cisco.com/as/token.oauth2"
    response = requests.post(url, verify=False, data={"grant_type": "client_credentials"},
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    params={"client_id":client_id,"client_secret":client_secret})
    token = response.json()["token_type"] + " " + response.json()["access_token"]
    headers = {"Authorization": token}

    for entry in devicesdf.values:
        try:
            os = entry[2]
            version = entry[4]
            if os not in osdict.keys():
                osdict[os] = []
                if version not in osdict[os]:
                    osdict[os].append(version)
                elif version in osdict[os]:
                    pass
            elif os in osdict.keys():
                if version not in osdict[os]:
                    osdict[os].append(version)
                elif version in osdict[os]:
                    pass
        except(KeyError):
            pass
    
    total = 0
    for os in osdict.keys():
        total = total + len(osdict[os])

    with tqdm(total=total, desc="Extracting psirt data") as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            ejecucion = {executor.submit(apicall,os,headers,osdict,OSdata,pbar): os for os in osdict.keys()}
        for output in concurrent.futures.as_completed(ejecucion):
            output.result()