#!/usr/bin/env python3

import concurrent.futures, requests
from ratelimit import RateLimitException, limits
from backoff import on_exception, expo
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from tqdm import tqdm
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

products,Bdata = {},[]

@on_exception(expo,RateLimitException,max_tries=5)
@limits(calls=10,period=1)
def apicall(series,headers,products,Bdata,pbar,errors):
    for os in products[series]["versions"]:
        url = f"https://api.cisco.com/bug/v3.0/bugs/product_series/{series}/affected_releases/{os}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            bug = response.json()
            if bug["bugs"] != []:
                for entry in bug["bugs"]:
                    Bdata.append({"ProductSeries":series,"OSversion":os,"BugID":entry["bug_id"],"Headline":entry["headline"],"Severity":entry["severity"],
                    "Status":entry["status"],"LastModifiedDate":entry["last_modified_date"],"KnownFixedReleases":entry["known_fixed_releases"]})
                last_page = response.json()["pagination_response_record"]["last_index"]
                for page in range(2,last_page+1):
                    url = f"https://api.cisco.com/bug/v3.0/bugs/product_series/{series}/affected_releases/{os}?page_index="+ str(page)
                    response = requests.get(url, headers=headers)
                    if response.status_code == 200:
                        bug = response.json()
                        for entry in bug["bugs"]:
                            Bdata.append({"ProductSeries":series,"OSversion":os,"BugID":entry["bug_id"],"Headline":entry["headline"],"Severity":entry["severity"],"Status":entry["status"]
                            ,"LastModifiedDate":entry["last_modified_date"],"KnownFixedReleases":entry["known_fixed_releases"]})
                    elif response.status_code != 200:
                        errorMessage = "HTTPError:"+str(response.status_code)
                        errors.append({"API":"Bug","id":series+os,"Error":errorMessage})
            elif bug["bugs"] == []:
                Bdata.append({"ProductSeries":series,"OSversion":os,"BugID":None,"Headline":None,"Severity":None,"Status":None
                ,"LastModifiedDate":None,"KnownFixedReleases":None})
        elif response.status_code != 200:
            errorMessage = "HTTPError:"+str(response.status_code)
            errors.append({"API":"Bug","id":series+os,"Error":errorMessage})
        
    pbar.update(1)

def bugdata(env_vars,devicesdf,products,productsdf,Bdata,errors):

    client_id = env_vars["client_id"]
    client_secret = env_vars["client_secret"]
    url = "https://cloudsso.cisco.com/as/token.oauth2"
    response = requests.post(url, verify=False, data={"grant_type": "client_credentials"},
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    params={"client_id":client_id,"client_secret":client_secret})
    token = response.json()["token_type"] + " " + response.json()["access_token"]
    headers = {"Authorization": token}
    
    for entry in productsdf.values:
        productid = entry[0]
        productseries = entry[2]
        if productseries not in products.keys():
            products[productseries] = {}
            products[productseries]["versions"] = []
            for entry in devicesdf.values:
                try:
                    productid_ = entry[1]
                    version = entry[4]
                    if productid == productid_ and version not in products[productseries]["versions"]:
                        products[productseries]["versions"].append(version)
                except(KeyError):
                    pass
        elif productseries in products.keys():
            for entry in devicesdf.values:
                try:
                    productid_ = entry[1]
                    version = entry[4]
                    if productid == productid_ and version not in products[productseries]["versions"]:
                        products[productseries]["versions"].append(version)
                except(KeyError):
                    pass

    with tqdm(total=len(products), desc="Extracting bug data") as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            ejecucion = {executor.submit(apicall,series,headers,products,Bdata,pbar,errors): series for series in products.keys()}
        for output in concurrent.futures.as_completed(ejecucion):
            output.result()