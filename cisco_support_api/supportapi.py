#!/usr/bin/env python3
#v1.0.5

import requests
from ratelimit import RateLimitException, limits
from backoff import on_exception, expo
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from tqdm import tqdm
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

Edata,SFdata,Sdata,Pdata = [],[],[],[]
productsid =  []
supportdict = {}

@on_exception(expo,RateLimitException,max_tries=5)
@limits(calls=5,period=1)
def eoxdata(headers,serialnumbers,Edata):

    with tqdm(total=len(serialnumbers), desc="Extracting eox data") as pbar:
        for id in serialnumbers:
            url = f"https://api.cisco.com/supporttools/eox/rest/5/EOXBySerialNumber/1/{id}?responseencoding=json"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                eox = response.json()["EOXRecord"][0]
                if "EOXError" in eox.keys():
                    if "does not exist" in eox["EOXError"]["ErrorDescription"]:
                        product =  eox["EOXError"]["ErrorDataValue"]
                        productsid.append(product)
                        EndOfSaleDate = "N/A"
                        LastDateOfSupport = "N/A"
                        EOXMigrationDetails = "N/A"
                elif "EOXError" not in eox.keys():
                    product =  eox["EOLProductID"]
                    productsid.append(product)
                    EndOfSaleDate =  eox["EndOfSaleDate"]["value"]
                    LastDateOfSupport = eox["LastDateOfSupport"]["value"]
                    EOXMigrationDetails = eox["EOXMigrationDetails"]["MigrationProductId"]
                    pass
                Edata.append({"ProductID":id,"EndOfSaleDate":EndOfSaleDate,"LastDateOfSupport":LastDateOfSupport,
                "EOXMigrationDetails":EOXMigrationDetails})
            elif response.status_code != 200:
                errorMessage = "HTTPError:"+str(response.status_code)
                Edata.append({"ProductID":id,"EndOfSaleDate":errorMessage,"LastDateOfSupport":errorMessage,
                "EOXMigrationDetails":errorMessage})
            pbar.update(1)

@on_exception(expo,RateLimitException,max_tries=5)
@limits(calls=5,period=1)
def serialdata(headers,serialnumbers,Sdata):

    with tqdm(total=len(serialnumbers), desc="Extracting serial data") as pbar:
        for number in serialnumbers:
            url = f"https://api.cisco.com/sn2info/v2/coverage/summary/serial_numbers/{number}" 
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                try:
                    serial = response.json()["serial_numbers"][0]
                    customer = serial["contract_site_customer_name"]
                    contractEndDate = serial["covered_product_line_end_date"]
                    isCovered = serial["is_covered"]
                except(KeyError):
                    customer = "N/A"
                    contractEndDate = "N/A"
                    isCovered = "N/A"
                Sdata.append({"SerialNumber":number,"Customer":customer,
                "ContractEndDate":contractEndDate,"IsCovered":isCovered})
            elif response.status_code != 200:
                errorMessage = "HTTPError:"+str(response.status_code)
                Sdata.append({"SerialNumber":number,"Customer":errorMessage,
                "ContractEndDate":errorMessage,"IsCovered":errorMessage})
            pbar.update(1)

@on_exception(expo,RateLimitException,max_tries=5)
@limits(calls=10,period=1)
def productdata(headers,productsid,Pdata):

    with tqdm(total=len(productsid), desc="Extracting product data") as pbar:
        for id in productsid:
            url = f"https://api.cisco.com/product/v1/information/product_ids/{id}"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                product = response.json()["product_list"][0]
                ProductReleaseDate = product["release_date"]
                ProductSeries = product["product_series"].replace(" ","%20")
                Pdata.append({"ProductID":id,"ProductReleaseDate":ProductReleaseDate,"ProductSeries":ProductSeries})
            elif response.status_code != 200:
                errorMessage = "HTTPError:"+str(response.status_code)
                Pdata.append({"ProductID":id,"ProductReleaseDate":errorMessage,"ProductSeries":errorMessage})
            pbar.update(1)
    
@on_exception(expo,RateLimitException,max_tries=5)
@limits(calls=10,period=1)
def softwaredata(headers,productsid,SFdata):

    with tqdm(total=len(productsid), desc="Extracting software data") as pbar:
        for id in productsid:
            url = f"https://api.cisco.com/software/suggestion/v2/suggestions/software/productIds/{id}"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                software = response.json()["productList"]
                for entry in software:
                    try:
                        if entry["suggestions"][0]["isSuggested"] == "Y":
                            RosVersion = entry["suggestions"][0]["releaseFormat1"]
                            SreleaseDate = entry["suggestions"][0]["releaseDate"]
                            imageName = entry["suggestions"][0]["images"][0]["imageName"]
                        elif entry["suggestions"][0]["isSuggested"] == "N":
                            RosVersion = "Validate"
                            SreleaseDate = "Validate"
                            imageName = "Validate"
                        SFdata.append({"ProductID":id,"RecommendedOSversion":RosVersion,"SoftwareReleaseDate":SreleaseDate,
                        "ImageName":imageName})
                    except(KeyError,UnboundLocalError):
                        RosVersion = "Validate"
                        SreleaseDate = "Validate"
                        imageName = "Validate"
                        SFdata.append({"ProductID":id,"RecommendedOSversion":RosVersion,"SoftwareReleaseDate":SreleaseDate,
                        "ImageName":imageName})
            elif response.status_code != 200:
                errorMessage = "HTTPError:"+str(response.status_code)
                SFdata.append({"ProductID":id,"RecommendedOSversion":errorMessage,"SoftwareReleaseDate":errorMessage,
                "ImageName":errorMessage})
            pbar.update(1)

def supportdata(env_vars,devicesdf,supportdict):

    client_id = env_vars["client_id"]
    client_secret = env_vars["client_secret"]
    url = "https://cloudsso.cisco.com/as/token.oauth2"
    response = requests.post(url, verify=False, data={"grant_type": "client_credentials"},
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    params={"client_id":client_id,"client_secret":client_secret})
    token = response.json()["token_type"] + " " + response.json()["access_token"]
    headers = {"Authorization": token}

    serialnumbers = list(devicesdf["SerialNumber"].unique())

    eoxdata(headers,serialnumbers,Edata)
    serialdata(headers,productsid,Sdata)
    softwaredata(headers,productsid,SFdata)
    productdata(headers,productsid,Pdata)
    
    supportdict["eoxdata"] = Edata
    supportdict["softwaredata"] = SFdata
    supportdict["serialdata"] = Sdata 
    supportdict["productdata"] = Pdata