#!/usr/bin/env python3
#v1.0.1

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
productnames = {}

@on_exception(expo,RateLimitException,max_tries=5)
@limits(calls=10,period=1)
def bugdata(header,productnames):

    file = open("devicedata.json","r")
    devicedata = json.loads(file.read())
    file = open("productdata.json","r")
    productdata = json.loads(file.read())

    for entry in devicedata.keys():
        try:
            if devicedata[entry]["model"] not in productnames:
                productnames[devicedata[entry]["model"]] = {}
                productnames[devicedata[entry]["model"]]["product_name"] = productdata[devicedata[entry]["model"]]["product_name"]
                productnames[devicedata[entry]["model"]]["versions"] = []
                if devicedata[entry]["version"] not in productnames[devicedata[entry]["model"]]["versions"]:
                    productnames[devicedata[entry]["model"]]["versions"].append(devicedata[entry]["version"])
                elif devicedata[entry]["version"] in productnames[devicedata[entry]["model"]]["versions"]:
                    pass
            elif devicedata[entry]["model"] in productnames:
                if devicedata[entry]["version"] not in productnames[devicedata[entry]["model"]]["versions"]:
                    productnames[devicedata[entry]["model"]]["versions"].append(devicedata[entry]["version"])
                elif devicedata[entry]["version"] in productnames[devicedata[entry]["model"]]["versions"]:
                    pass
        except(KeyError):
            pass

    data_file = open("bugdata.csv","w", newline='',encoding="utf-8")
    first_row = ["product_id","os_version","bug_id","headline","severity","status","last_modified_date","known_fixed_releases"]
    writer = csv.DictWriter(data_file, fieldnames=first_row, restval="Error")
    writer.writeheader()

    for id in productnames:
        name = productnames[id]["product_name"]
        for os in productnames[id]["versions"]:
            url = f"https://api.cisco.com/bug/v3.0/bugs/product_series/{name}/affected_releases/{os}"
            response = requests.get(url, headers=header)
            if response.status_code == 200:
                bugpage1 = response.json()
                if bugpage1["bugs"] != []:
                    for entry in bugpage1["bugs"]:
                        if entry["status"] == "O":
                            status = "Open"
                        elif entry["status"] == "F":
                            status = "Fixed"
                        elif entry["status"] == "T":
                            status = "Terminated"
                        writer.writerow({"product_id":id,"os_version":os,"bug_id":entry["bug_id"],"headline":entry["headline"],"severity":entry["severity"],"status":status
                        ,"last_modified_date":entry["last_modified_date"],"known_fixed_releases":entry["known_fixed_releases"]})
                    last_page = response.json()["pagination_response_record"]["last_index"]
                    for page in range(2,last_page+1):
                        url = f"https://api.cisco.com/bug/v3.0/bugs/product_series/{name}/affected_releases/{os}?page_index="+ str(page)
                        response = requests.get(url, headers=header)
                        if response.status_code == 200:
                            bug = response.json()
                            for entry in bug["bugs"]:
                                if entry["status"] == "O":
                                    status = "Open"
                                elif entry["status"] == "F":
                                    status = "Fixed"
                                elif entry["status"] == "T":
                                    status = "Terminated"
                                writer.writerow({"product_id":id,"os_version":os,"bug_id":entry["bug_id"],"headline":entry["headline"],"severity":entry["severity"],"status":status
                                ,"last_modified_date":entry["last_modified_date"],"known_fixed_releases":entry["known_fixed_releases"]})
                        elif response.status_code != 200:
                            print(f"Bug API, HTTP error code {response.status_code}, device model {id}")
                elif bugpage1["bugs"] == []:
                    writer.writerow({"product_id":id,"os_version":os,"bug_id":"no data","headline":"no data","severity":"no data","status":"no data"
                    ,"last_modified_date":"no data","known_fixed_releases":"no data"})
            elif response.status_code != 200:
                print(f"Bug API, HTTP error code {response.status_code}, device model {id}")
                
    data_file.close()
