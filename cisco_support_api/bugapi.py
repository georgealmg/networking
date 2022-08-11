#!/usr/bin/env python3
#v1.0.4

import concurrent.futures, requests
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
def apicall(id,header,products,Bdata,pbar):

    url = f"https://api.cisco.com/bug/v3.0/bugs/products/product_id/{id}"
    response = requests.get(url, headers=header)
    if response.status_code == 200:
        bug = response.json()
        if bug["bugs"] != []:
            for entry in bug["bugs"]:
                for os in products[id]["versions"]:
                    if os in entry["known_affected_releases"]:
                        Bdata.append({"ProductID":id,"OSversion":os,"BugID":entry["bug_id"],"headline":entry["headline"],"severity":entry["severity"],"status":entry["status"]
                        ,"LastModifiedDate":entry["last_modified_date"],"KnownFixedReleases":entry["known_fixed_releases"]})
                    elif os not in entry["known_affected_releases"]:
                        pass
            last_page = response.json()["pagination_response_record"]["last_index"]
            for page in range(2,last_page+1):
                url = f"https://api.cisco.com/bug/v3.0/bugs/products/product_id/{id}?page_index="+ str(page)
                response = requests.get(url, headers=header)
                if response.status_code == 200:
                    bug = response.json()
                    for entry in bug["bugs"]:
                        for os in products[id]["versions"]:
                            if os in entry["known_affected_releases"]:
                                Bdata.append({"ProductID":id,"OSversion":os,"BugID":entry["bug_id"],"headline":entry["headline"],"severity":entry["severity"],"status":entry["status"]
                                ,"LastModifiedDate":entry["last_modified_date"],"KnownFixedReleases":entry["known_fixed_releases"]})
                            elif os not in entry["known_affected_releases"]:
                                pass
                elif response.status_code != 200:
                    errorMessage = "HTTPError:"+str(response.status_code)
                    Bdata.append({"ProductID":id,"OSversion":errorMessage,"BugID":errorMessage,"headline":errorMessage,"severity":errorMessage,"status":errorMessage
                    ,"LastModifiedDate":errorMessage,"KnownFixedReleases":errorMessage})
    elif response.status_code != 200:
        errorMessage = "HTTPError:"+str(response.status_code)
        Bdata.append({"ProductID":id,"OSversion":errorMessage,"BugID":errorMessage,"headline":errorMessage,"severity":errorMessage,"status":errorMessage
        ,"LastModifiedDate":errorMessage,"KnownFixedReleases":errorMessage})

    pbar.update(1)

def bugdata(devicesdf,header,products,Bdata):

    for entry in devicesdf.values:
        try:
            productid = entry[2]
            version = entry[5]
            if productid not in products.keys():
                products[productid] = {}
                products[productid]["versions"] = []
                products[productid]["versions"].append(version)
            elif productid in products.keys() and version not in products[productid]["versions"]:
                products[productid]["versions"].append(version)
        except(KeyError):
            pass

    with tqdm(total=len(products), desc="Extracting bug data") as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            ejecucion = {executor.submit(apicall,id,header,products,Bdata,pbar): id for id in products.keys()}
        for output_ios in concurrent.futures.as_completed(ejecucion):
            output_ios.result()
            pbar.update(1)