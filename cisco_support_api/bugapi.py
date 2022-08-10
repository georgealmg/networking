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
products = {}
Bdata = []

@on_exception(expo,RateLimitException,max_tries=5)
@limits(calls=10,period=1)
def bugdata(devicesdf,header,products,Bdata):

    for entry in devicesdf.values:
        try:
            productid = entry[2]
            version = entry[5]
            if productid not in products.keys():
                products[productid] = {}
                products[productid]["versions"] = []
                products[productid]["versions"].append(version)
            elif productid in products.keys() and os not in products[productid]["versions"]:
                products[productid]["versions"].append(version)
        except(KeyError):
            pass

    with tqdm(total=len(products), desc="Extracting bug data") as pbar:
        for id in products.keys():
            for os in products[id]["versions"]:
                url = f"https://api.cisco.com/bug/v3.0/bugs/products/product_id/{id}"
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
                            if os in entry["known_affected_releases"]:
                                Bdata.append({"product_id":id,"os_version":os,"bug_id":entry["bug_id"],"headline":entry["headline"],"severity":entry["severity"],"status":status
                                ,"last_modified_date":entry["last_modified_date"],"known_fixed_releases":entry["known_fixed_releases"]})
                        last_page = response.json()["pagination_response_record"]["last_index"]
                        for page in range(2,last_page+1):
                            url = f"https://api.cisco.com/bug/v3.0/bugs/products/product_id/{id}?page_index="+ str(page)
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
                                    if os in entry["known_affected_releases"]:
                                        Bdata.append({"product_id":id,"os_version":os,"bug_id":entry["bug_id"],"headline":entry["headline"],"severity":entry["severity"],"status":status
                                        ,"last_modified_date":entry["last_modified_date"],"known_fixed_releases":entry["known_fixed_releases"]})
                            elif response.status_code != 200:
                                errorMessage = "HTTPError:"+str(response.status_code)
                                Bdata.append({"product_id":id,"os_version":os,"bug_id":errorMessage,"headline":errorMessage,"severity":errorMessage,"status":errorMessage
                                ,"last_modified_date":errorMessage,"known_fixed_releases":errorMessage})
                    elif bugpage1["bugs"] == []:
                        Bdata.append({"product_id":id,"os_version":os,"bug_id":"no data","headline":"no data","severity":"no data","status":"no data"
                        ,"last_modified_date":"no data","known_fixed_releases":"no data"})
                elif response.status_code != 200:
                    errorMessage = "HTTPError:"+str(response.status_code)
                    Bdata.append({"product_id":id,"os_version":os,"bug_id":errorMessage,"headline":errorMessage,"severity":errorMessage,"status":errorMessage
                    ,"last_modified_date":errorMessage,"known_fixed_releases":errorMessage})
            pbar.update(1)