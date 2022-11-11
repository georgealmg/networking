#!/usr/bin/env python3

import requests, numpy as np
from ratelimit import RateLimitException, limits
from backoff import on_exception, expo
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from tqdm import tqdm
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

Edata,SFdata,Sdata,Pdata = [],[],[],[]
supportdict = {}

@on_exception(expo,RateLimitException,max_tries=5)
@limits(calls=5,period=1)
def serialdata(headers,serialnumbers,Sdata,errors):

    serial_array = np.array_split(serialnumbers,(len(serialnumbers)//50)+1)
    with tqdm(total=len(serial_array), desc="Extracting serial data") as pbar:
        for entry in serial_array:
            number = str(entry).replace("'","").replace(" ",",").replace("["," ").replace("]","").replace("\n","").replace(" ","")
            url = f"https://api.cisco.com/sn2info/v2/coverage/summary/serial_numbers/{number}"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                for record in response.json()["serial_numbers"]:
                    serial = record["sr_no"]
                    customer = record["contract_site_customer_name"]
                    contractEndDate = record["covered_product_line_end_date"]
                    isCovered = record["is_covered"]
                    Sdata.append({"SerialNumber":serial,"Customer":customer,
                    "ContractEndDate":contractEndDate,"IsCovered":isCovered})
            elif response.status_code != 200:
                errorMessage = "HTTPError:"+str(response.status_code)
                errors.append({"API":"Serial","id":number,"Error":errorMessage})
            pbar.update(1)

@on_exception(expo,RateLimitException,max_tries=5)
@limits(calls=5,period=1)
def eoxdata(headers,productsid,Edata,errors):

    product_array = np.array_split(productsid,(len(productsid)//20)+1)
    with tqdm(total=len(product_array), desc="Extracting eox data") as pbar:
        for entry in product_array:
            id = str(entry).replace("'","").replace(" ",",").replace("["," ").replace("]","").replace("\n","").replace(" ","")
            url = f"https://api.cisco.com/supporttools/eox/rest/5/EOXByProductID/1/{id}"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                for record in response.json()["EOXRecord"]:
                    if "EOXError" in record.keys():
                        if "does not exist" in record["EOXError"]["ErrorDescription"]:
                            product = record["EOXInputValue"]
                            EndOfSaleDate = None
                            LastDateOfSupport = None
                            EOXMigrationDetails = None
                    elif "EOXError" not in record.keys():
                        product = record["EOXInputValue"]
                        EndOfSaleDate =  record["EndOfSaleDate"]["value"]
                        LastDateOfSupport = record["LastDateOfSupport"]["value"]
                        EOXMigrationDetails = record["EOXMigrationDetails"]["MigrationProductId"]
                    Edata.append({"ProductID":product,"EndOfSaleDate":EndOfSaleDate,"LastDateOfSupport":LastDateOfSupport,
                    "EOXMigrationDetails":EOXMigrationDetails})
            elif response.status_code != 200:
                errorMessage = "HTTPError:"+str(response.status_code)
                errors.append({"API":"Eox","id":id,"Error":errorMessage})
            pbar.update(1)

@on_exception(expo,RateLimitException,max_tries=5)
@limits(calls=10,period=1)
def productdata(headers,productsid,Pdata,errors):

    product_array = np.array_split(productsid,(len(productsid)//5)+1)
    with tqdm(total=len(product_array), desc="Extracting product data") as pbar:
        for entry in product_array:
            id = str(entry).replace("'","").replace(" ",",").replace("["," ").replace("]","").replace("\n","").replace(" ","")
            url = f"https://api.cisco.com/product/v1/information/product_ids/{id}"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                for record in response.json()["product_list"]:
                    product = record["product_id"]
                    ProductReleaseDate = record["release_date"]
                    ProductSeries = record["product_series"].replace(" ","%20")
                    Pdata.append({"ProductID":product,"ProductReleaseDate":ProductReleaseDate,"ProductSeries":ProductSeries})
            elif response.status_code != 200:
                errorMessage = "HTTPError:"+str(response.status_code)
                errors.append({"API":"Product","id":id,"Error":errorMessage})
            pbar.update(1)
    
@on_exception(expo,RateLimitException,max_tries=5)
@limits(calls=10,period=1)
def softwaredata(headers,productsid,SFdata,errors):

    product_array = np.array_split(productsid,(len(productsid)//10)+1)
    with tqdm(total=len(product_array), desc="Extracting software data") as pbar:
        for entry in product_array:
            id = str(entry).replace("'","").replace(" ",",").replace("["," ").replace("]","").replace("\n","").replace(" ","")
            url = f"https://api.cisco.com/software/suggestion/v2/suggestions/software/productIds/{id}"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                software = response.json()["productList"]
                for record in software:
                    product = record["product"]["basePID"]
                    try:
                        for subrecord in record["suggestions"]:
                            if subrecord["isSuggested"] == "Y":
                                RosVersion = subrecord["releaseFormat1"]
                                SreleaseDate = subrecord["releaseDate"]
                                imageName = subrecord["images"][0]["imageName"]
                            elif subrecord["isSuggested"] == "":
                                RosVersion = None
                                SreleaseDate = None
                                imageName = None
                            SFdata.append({"ProductID":product,"RecommendedOSversion":RosVersion,"SoftwareReleaseDate":SreleaseDate,
                            "ImageName":imageName})
                    except(KeyError,UnboundLocalError):
                        RosVersion = None
                        SreleaseDate = None
                        imageName = None
                        SFdata.append({"ProductID":product,"RecommendedOSversion":RosVersion,"SoftwareReleaseDate":SreleaseDate,
                        "ImageName":imageName})
            elif response.status_code != 200:
                errorMessage = "HTTPError:"+str(response.status_code)
                errors.append({"API":"Software","id":id,"Error":errorMessage})
            pbar.update(1)

def supportdata(env_vars,devicesdf,supportdict,errors):

    client_id = env_vars["client_id"]
    client_secret = env_vars["client_secret"]
    url = "https://cloudsso.cisco.com/as/token.oauth2"
    response = requests.post(url, verify=False, data={"grant_type": "client_credentials"},
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    params={"client_id":client_id,"client_secret":client_secret})
    token = response.json()["token_type"] + " " + response.json()["access_token"]
    headers = {"Authorization": token}

    serialnumbers = devicesdf["SerialNumber"].values
    productsid = devicesdf["ProductID"].unique()

    serialdata(headers,serialnumbers,Sdata,errors)
    eoxdata(headers,productsid,Edata,errors)
    softwaredata(headers,productsid,SFdata,errors)
    productdata(headers,productsid,Pdata,errors)
    
    supportdict["eoxdata"] = Edata
    supportdict["softwaredata"] = SFdata
    supportdict["serialdata"] = Sdata 
    supportdict["productdata"] = Pdata