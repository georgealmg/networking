#!/usr/bin/env python3
#v1.0.0

import csv, json, requests
from ratelimit import RateLimitException, limits
from backoff import on_exception, expo
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


url = "https://cloudsso.cisco.com/as/token.oauth2"
response = requests.post(url, verify=False, data={"grant_type": "client_credentials"},
headers={"Content-Type": "application/x-www-form-urlencoded"},
params={"client_id": "", "client_secret":""})
token = response.json()["token_type"] + " " + response.json()["access_token"]
header = {"Authorization": token}

file = open("devicedata.json","r")
devicedata = json.loads(file.read())
os_dict = {}

for entry in devicedata.keys():
    try:
        if devicedata[entry]["os"] not in os_dict:
            os_dict[devicedata[entry]["os"]] = []
            if devicedata[entry]["version"] not in os_dict[devicedata[entry]["os"]]:
                os_dict[devicedata[entry]["os"]].append(devicedata[entry]["version"])
            elif devicedata[entry]["version"] in os_dict[devicedata[entry]["os"]]:
                pass
        elif devicedata[entry]["os"] in os_dict:
            if devicedata[entry]["version"] not in os_dict[devicedata[entry]["os"]]:
                os_dict[devicedata[entry]["os"]].append(devicedata[entry]["version"])
            elif devicedata[entry]["version"] in os_dict[devicedata[entry]["os"]]:
                pass
    except(KeyError):
        pass

@on_exception(expo,RateLimitException,max_tries=5)
@limits(calls=10,period=1)
def psirtdata(header,os_dict):

    data_file = open("psirtdata.csv","w", newline='',encoding="utf-8")
    first_row = ["os_family","os_version","bug_id","advisoryTitle","cves","cwe","cve_version","status",
    "firstPublished","lastUpdated","severity","affected_release","first_fixed","url"]
    writer = csv.DictWriter(data_file, fieldnames=first_row, restval="Error")
    writer.writeheader()

    for version in os_dict["ios"]:
        url = f"https://api.cisco.com/security/advisories/ios?version={version}"
        response = requests.get(url, headers=header)
        if response.status_code == 200:
            psirt = response.json()
            if "errorCode" not in psirt.keys():
                psirt = response.json()["advisories"]
                for entry in psirt:
                    writer.writerow({"os_family":"ios","os_version":version,"bug_id":entry["bugIDs"],"advisoryTitle":entry["advisoryTitle"],"cves":entry["cves"]
                    ,"cwe":entry["cwe"],"cve_version":entry["version"],"status":entry["status"],"firstPublished":entry["firstPublished"],
                    "lastUpdated":entry["lastUpdated"],"severity":entry["sir"],"affected_release":entry["iosRelease"],"first_fixed":entry["firstFixed"]
                    ,"url":entry["publicationUrl"]})
            elif "errorCode" in psirt.keys():
                    writer.writerow({"os_family":"ios","os_version":version,"bug_id":"N/A","advisoryTitle":"N/A","cves":"N/A"
                    ,"cwe":"N/A","cve_version":"N/A","status":"N/A","firstPublished":"N/A",
                    "lastUpdated":"N/A","severity":"N/A","affected_release":"N/A","first_fixed":"N/A"
                    ,"url":"N/A"})
            elif response.status_code != 200:
                print(f"PSIRT API, HTTP error code {response.status_code}, ios version {id}")

    for version in os_dict["iosxe"]:
        url = f"https://api.cisco.com/security/advisories/iosxe?version={version}"
        response = requests.get(url, headers=header)
        if response.status_code == 200:
            psirt = response.json()
            if "errorCode" not in psirt.keys():
                psirt = response.json()["advisories"]
                for entry in psirt:
                    writer.writerow({"os_family":"iosxe","os_version":version,"bug_id":entry["bugIDs"],"advisoryTitle":entry["advisoryTitle"],"cves":entry["cves"]
                    ,"cwe":entry["cwe"],"cve_version":entry["version"],"status":entry["status"],"firstPublished":entry["firstPublished"],
                    "lastUpdated":entry["lastUpdated"],"severity":entry["sir"],"affected_release":entry["iosRelease"],"first_fixed":entry["firstFixed"]
                    ,"url":entry["publicationUrl"]})
            elif "errorCode" in psirt.keys():
                    writer.writerow({"os_family":"iosxe","os_version":version,"bug_id":"N/A","advisoryTitle":"N/A","cves":"N/A"
                    ,"cwe":"N/A","cve_version":"N/A","status":"N/A","firstPublished":"N/A",
                    "lastUpdated":"N/A","severity":"N/A","affected_release":"N/A","first_fixed":"N/A"
                    ,"url":"N/A"})
            elif response.status_code != 200:
                print(f"PSIRT API, HTTP error code {response.status_code}, iosxe version {id}")

    for version in os_dict["nxos"]:
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
                    writer.writerow({"os_family":"nxos","os_version":version,"bug_id":entry["bugIDs"],"advisoryTitle":entry["advisoryTitle"],"cves":entry["cves"]
                    ,"cwe":entry["cwe"],"cve_version":entry["version"],"status":entry["status"],"firstPublished":entry["firstPublished"],
                    "lastUpdated":entry["lastUpdated"],"severity":entry["sir"],"affected_release":entry["iosRelease"],"first_fixed":first_fixed
                    ,"url":entry["publicationUrl"]})
            elif "errorCode" in psirt.keys():
                    writer.writerow({"os_family":"nxos","os_version":version,"bug_id":"N/A","advisoryTitle":"N/A","cves":"N/A"
                    ,"cwe":"N/A","cve_version":"N/A","status":"N/A","firstPublished":"N/A",
                    "lastUpdated":"N/A","severity":"N/A","affected_release":"N/A","first_fixed":"N/A"
                    ,"url":"N/A"})
            elif response.status_code != 200:
                print(f"PSIRT API, HTTP error code {response.status_code}, iosxe version {id}")

    data_file.close()
# psirtdata(header,os_dict)