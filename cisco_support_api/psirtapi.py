#!/usr/bin/env python3

import concurrent.futures, requests
from ratelimit import RateLimitException, limits
from backoff import on_exception, expo
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from tqdm import tqdm
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

osdict,OSdata = {},[]

@on_exception(expo,RateLimitException,max_tries=5)
@limits(calls=10,period=1)
def apicall(os,headers,osdict,OSdata,pbar,errors):
    for version in osdict[os]:
        url = f"https://api.cisco.com/security/advisories/{os}?version={version}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            psirt = response.json()
            if "errorCode" not in psirt.keys():
                psirt = response.json()["advisories"]
                for entry in psirt:
                    if "firstFixed" in entry.keys():
                        OSdata.append({"OSfamily":os,"OSversion":version,"BugID":str(entry["bugIDs"]),"advisoryTitle":entry["advisoryTitle"],"cves":str(entry["cves"])
                        ,"cwe":str(entry["cwe"]),"status":entry["status"],"firstPublished":entry["firstPublished"],
                        "lastUpdated":entry["lastUpdated"],"severity":entry["sir"],"firstFixed":str(entry["firstFixed"])
                        ,"url":entry["publicationUrl"]})
                    elif "firstFixed" not in entry.keys():
                        OSdata.append({"OSfamily":os,"OSversion":version,"BugID":str(entry["bugIDs"]),"advisoryTitle":entry["advisoryTitle"],"cves":str(entry["cves"])
                        ,"cwe":str(entry["cwe"]),"status":entry["status"],"firstPublished":entry["firstPublished"],
                        "lastUpdated":entry["lastUpdated"],"severity":entry["sir"],"firstFixed":entry["platforms"][0]["firstFixes"][0]["name"]
                        ,"url":entry["publicationUrl"]})
            elif "errorCode" in psirt.keys():
                    OSdata.append({"OSfamily":os,"OSversion":version,"BugID":None,"advisoryTitle":None,"cves":None
                    ,"cwe":None,"status":None,"firstPublished":None,
                    "lastUpdated":None,"severity":None,"firstFixed":None
                    ,"url":None})
        elif response.status_code != 200:
            errorMessage = "HTTPError:"+str(response.status_code)
            errors.append({"API":"Bug","id":version+os,"Error":errorMessage})
    
        pbar.update(1)

def psirtdata(env_vars,devicesdf,osdict,OSdata,errors):

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
            os = entry[3]
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
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            ejecucion = {executor.submit(apicall,os,headers,osdict,OSdata,pbar,errors): os for os in osdict.keys()}
        for output in concurrent.futures.as_completed(ejecucion):
            output.result()