#!/usr/bin/env python3
#v1.0.3

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
            if entry[4] not in osdict.keys():
                osdict[entry[4]] = []
                if entry[5] not in osdict[entry[4]]:
                    osdict[entry[4]].append(entry[5])
                elif entry[5] in osdict[entry[4]]:
                    pass
            elif entry[4] in osdict.keys():
                if entry[5] not in osdict[entry[4]]:
                    osdict[entry[4]].append(entry[5])
                elif entry[5] in osdict[entry[4]]:
                    pass
        except(KeyError):
            pass
    
    with tqdm(total=len(osdict.values()), desc="Extracting psirt data") as pbar:
        if "ios" in osdict.keys(): 
            for version in osdict["ios"]:
                url = f"https://api.cisco.com/security/advisories/ios?version={version}"
                response = requests.get(url, headers=header)
                if response.status_code == 200:
                    psirt = response.json()
                    if "errorCode" not in psirt.keys():
                        psirt = response.json()["advisories"]
                        for entry in psirt:
                            OSdata.append({"OSfamily":"ios","OSversion":version,"bug_id":str(entry["bugIDs"]),"advisoryTitle":entry["advisoryTitle"],"cves":str(entry["cves"])
                            ,"cwe":str(entry["cwe"]),"cveVersion":entry["version"],"status":entry["status"],"firstPublished":entry["firstPublished"],
                            "lastUpdated":entry["lastUpdated"],"severity":entry["sir"],"affected_release":str(entry["iosRelease"]),"first_fixed":str(entry["firstFixed"])
                            ,"url":entry["publicationUrl"]})
                    elif "errorCode" in psirt.keys():
                            OSdata.append({"OSfamily":"ios","OSversion":version,"bug_id":"N/A","advisoryTitle":"N/A","cves":"N/A"
                            ,"cwe":"N/A","cveVersion":"N/A","status":"N/A","firstPublished":"N/A",
                            "lastUpdated":"N/A","severity":"N/A","affected_release":"N/A","first_fixed":"N/A"
                            ,"url":"N/A"})
                    elif response.status_code != 200:
                        errorMessage = "HTTPError:"+str(response.status_code)
                        OSdata.append({"OSfamily":"ios","OSversion":version,"bug_id":errorMessage,"advisoryTitle":errorMessage,"cves":errorMessage
                        ,"cwe":errorMessage,"cveVersion":errorMessage,"status":errorMessage,"firstPublished":errorMessage,
                        "lastUpdated":errorMessage,"severity":errorMessage,"affected_release":errorMessage,"first_fixed":errorMessage
                        ,"url":errorMessage})
        elif "ios" not in osdict.keys():
            pass
        
        if "iosxe" in osdict.keys():
            for version in osdict["iosxe"]:
                url = f"https://api.cisco.com/security/advisories/iosxe?version={version}"
                response = requests.get(url, headers=header)
                if response.status_code == 200:
                    psirt = response.json()
                    if "errorCode" not in psirt.keys():
                        psirt = response.json()["advisories"]
                        for entry in psirt:
                            OSdata.append({"OSfamily":"iosxe","OSversion":version,"bug_id":str(entry["bugIDs"]),"advisoryTitle":entry["advisoryTitle"],"cves":str(entry["cves"])
                            ,"cwe":str(entry["cwe"]),"cveVersion":entry["version"],"status":entry["status"],"firstPublished":entry["firstPublished"],
                            "lastUpdated":entry["lastUpdated"],"severity":entry["sir"],"affected_release":str(entry["iosRelease"]),"first_fixed":str(entry["firstFixed"])
                            ,"url":entry["publicationUrl"]})
                    elif "errorCode" in psirt.keys():
                            OSdata.append({"OSfamily":"iosxe","OSversion":version,"bug_id":"N/A","advisoryTitle":"N/A","cves":"N/A"
                            ,"cwe":"N/A","cveVersion":"N/A","status":"N/A","firstPublished":"N/A",
                            "lastUpdated":"N/A","severity":"N/A","affected_release":"N/A","first_fixed":"N/A"
                            ,"url":"N/A"})
                    elif response.status_code != 200:
                        errorMessage = "HTTPError:"+str(response.status_code)
                        OSdata.append({"OSfamily":"ios","OSversion":version,"bug_id":errorMessage,"advisoryTitle":errorMessage,"cves":errorMessage
                        ,"cwe":errorMessage,"cveVersion":errorMessage,"status":errorMessage,"firstPublished":errorMessage,
                        "lastUpdated":errorMessage,"severity":errorMessage,"affected_release":errorMessage,"first_fixed":errorMessage
                        ,"url":errorMessage})
        elif "iosxe" not in osdict.keys():
            pass

        if "nxos" in osdict.keys():
            for version in osdict["nxos"]:
                url = f"https://api.cisco.com/security/advisories/nxos?version={version}"
                response = requests.get(url, headers=header)
                if response.status_code == 200:
                    psirt = response.json()
                    if "errorCode" not in psirt.keys():
                        psirt = response.json()["advisories"]
                        for entry in psirt:
                            first_fixed = []
                            for id in entry["platforms"]:
                                first_fixed.append(id["name"]+" os: "+id["firstFixes"][0]["name"])
                            OSdata.append({"OSfamily":"nxos","OSversion":version,"bug_id":str(entry["bugIDs"]),"advisoryTitle":entry["advisoryTitle"],"cves":str(entry["cves"])
                            ,"cwe":str(entry["cwe"]),"cveVersion":entry["version"],"status":entry["status"],"firstPublished":entry["firstPublished"],
                            "lastUpdated":entry["lastUpdated"],"severity":entry["sir"],"affected_release":str(entry["iosRelease"]),"first_fixed":str(entry["firstFixed"])
                            ,"url":entry["publicationUrl"]})
                    elif "errorCode" in psirt.keys():
                            OSdata.append({"OSfamily":"nxos","OSversion":version,"bug_id":"N/A","advisoryTitle":"N/A","cves":"N/A"
                            ,"cwe":"N/A","cveVersion":"N/A","status":"N/A","firstPublished":"N/A",
                            "lastUpdated":"N/A","severity":"N/A","affected_release":"N/A","first_fixed":"N/A"
                            ,"url":"N/A"})
                    elif response.status_code != 200:
                        errorMessage = "HTTPError:"+str(response.status_code)
                        OSdata.append({"OSfamily":"ios","OSversion":version,"bug_id":errorMessage,"advisoryTitle":errorMessage,"cves":errorMessage
                        ,"cwe":errorMessage,"cveVersion":errorMessage,"status":errorMessage,"firstPublished":errorMessage,
                        "lastUpdated":errorMessage,"severity":errorMessage,"affected_release":errorMessage,"first_fixed":errorMessage
                        ,"url":errorMessage})
        elif "nxos" not in osdict.keys():
            pass
        
        pbar.update(1)