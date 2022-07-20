#!/usr/bin/env python3
#v1.0.2

import csv, json, requests
from ratelimit import RateLimitException, limits
from backoff import on_exception, expo
from requests.packages.urllib3.exceptions import InsecureRequestWarning
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

    for entry in devicesdf.to_list():
        try:
            if entry["OS"] not in osdict.keys():
                osdict[entry["OS"]] = []
                if entry["Version"] not in osdict[entry["OS"]]:
                    osdict[entry["OS"]].append(entry["Version"])
                elif entry["Version"] in osdict[entry["OS"]]:
                    pass
            if entry["OS"] in osdict.keys():
                if entry["Version"] not in osdict[entry["OS"]]:
                    osdict[entry["OS"]].append(entry["Version"])
                elif entry["Version"] in osdict[entry["OS"]]:
                    pass
        except(KeyError):
            pass
    
    if "ios" in osdict.keys(): 
        for version in osdict["ios"]:
            url = f"https://api.cisco.com/security/advisories/ios?version={version}"
            response = requests.get(url, headers=header)
            if response.status_code == 200:
                psirt = response.json()
                if "errorCode" not in psirt.keys():
                    psirt = response.json()["advisories"]
                    for entry in psirt:
                        OSdata.append({"os_family":"ios","os_version":version,"bug_id":entry["bugIDs"],"advisoryTitle":entry["advisoryTitle"],"cves":entry["cves"]
                        ,"cwe":entry["cwe"],"cve_version":entry["version"],"status":entry["status"],"firstPublished":entry["firstPublished"],
                        "lastUpdated":entry["lastUpdated"],"severity":entry["sir"],"affected_release":entry["iosRelease"],"first_fixed":entry["firstFixed"]
                        ,"url":entry["publicationUrl"]})
                elif "errorCode" in psirt.keys():
                        OSdata.append({"os_family":"ios","os_version":version,"bug_id":"N/A","advisoryTitle":"N/A","cves":"N/A"
                        ,"cwe":"N/A","cve_version":"N/A","status":"N/A","firstPublished":"N/A",
                        "lastUpdated":"N/A","severity":"N/A","affected_release":"N/A","first_fixed":"N/A"
                        ,"url":"N/A"})
                elif response.status_code != 200:
                    errorMessage = "HTTPError:"+str(response.status_code)
                    OSdata.append({"os_family":"ios","os_version":version,"bug_id":errorMessage,"advisoryTitle":errorMessage,"cves":errorMessage
                    ,"cwe":errorMessage,"cve_version":errorMessage,"status":errorMessage,"firstPublished":errorMessage,
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
                        OSdata.append({"os_family":"iosxe","os_version":version,"bug_id":entry["bugIDs"],"advisoryTitle":entry["advisoryTitle"],"cves":entry["cves"]
                        ,"cwe":entry["cwe"],"cve_version":entry["version"],"status":entry["status"],"firstPublished":entry["firstPublished"],
                        "lastUpdated":entry["lastUpdated"],"severity":entry["sir"],"affected_release":entry["iosRelease"],"first_fixed":entry["firstFixed"]
                        ,"url":entry["publicationUrl"]})
                elif "errorCode" in psirt.keys():
                        OSdata.append({"os_family":"iosxe","os_version":version,"bug_id":"N/A","advisoryTitle":"N/A","cves":"N/A"
                        ,"cwe":"N/A","cve_version":"N/A","status":"N/A","firstPublished":"N/A",
                        "lastUpdated":"N/A","severity":"N/A","affected_release":"N/A","first_fixed":"N/A"
                        ,"url":"N/A"})
                elif response.status_code != 200:
                    errorMessage = "HTTPError:"+str(response.status_code)
                    OSdata.append({"os_family":"ios","os_version":version,"bug_id":errorMessage,"advisoryTitle":errorMessage,"cves":errorMessage
                    ,"cwe":errorMessage,"cve_version":errorMessage,"status":errorMessage,"firstPublished":errorMessage,
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
                        OSdata.append({"os_family":"nxos","os_version":version,"bug_id":entry["bugIDs"],"advisoryTitle":entry["advisoryTitle"],"cves":entry["cves"]
                        ,"cwe":entry["cwe"],"cve_version":entry["version"],"status":entry["status"],"firstPublished":entry["firstPublished"],
                        "lastUpdated":entry["lastUpdated"],"severity":entry["sir"],"affected_release":entry["iosRelease"],"first_fixed":first_fixed
                        ,"url":entry["publicationUrl"]})
                elif "errorCode" in psirt.keys():
                        OSdata.append({"os_family":"nxos","os_version":version,"bug_id":"N/A","advisoryTitle":"N/A","cves":"N/A"
                        ,"cwe":"N/A","cve_version":"N/A","status":"N/A","firstPublished":"N/A",
                        "lastUpdated":"N/A","severity":"N/A","affected_release":"N/A","first_fixed":"N/A"
                        ,"url":"N/A"})
                elif response.status_code != 200:
                    errorMessage = "HTTPError:"+str(response.status_code)
                    OSdata.append({"os_family":"ios","os_version":version,"bug_id":errorMessage,"advisoryTitle":errorMessage,"cves":errorMessage
                    ,"cwe":errorMessage,"cve_version":errorMessage,"status":errorMessage,"firstPublished":errorMessage,
                    "lastUpdated":errorMessage,"severity":errorMessage,"affected_release":errorMessage,"first_fixed":errorMessage
                    ,"url":errorMessage})
    elif "nxos" not in osdict.keys():
        pass