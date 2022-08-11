#!/usr/bin/env python3
#v1.0.4

import requests
from ratelimit import RateLimitException, limits
from backoff import on_exception, expo
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from tqdm import tqdm
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

url = "https://cloudsso.cisco.com/as/token.oauth2"
response = requests.post(url, verify=False, data={"grant_type": "client_credentials"},
headers={"Content-Type": "application/x-www-form-urlencoded"},
params={"client_id": "8e3ma3h3u7sfnmfn9h6nadky", "client_secret":"bqhyyPzsnjsVaW8PHcFw6TVh"})
token = response.json()["token_type"] + " " + response.json()["access_token"]
header = {"Authorization": token}
osdict = {}
OSdata = []

@on_exception(expo,RateLimitException,max_tries=5)
@limits(calls=10,period=1)
def psirtdata(devicesdf,header,osdict,OSdata):

    for entry in devicesdf.values:
        try:
            os = entry[4]
            version = entry[5]
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
        for os in osdict.keys(): 
            for version in osdict[os]:
                url = f"https://api.cisco.com/security/advisories/{os}?version={version}"
                response = requests.get(url, headers=header)
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