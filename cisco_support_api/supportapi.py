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
Edata,SFdata,Sdata,Pdata = [],[],[],[]
supportdict = {}

@on_exception(expo,RateLimitException,max_tries=5)
@limits(calls=5,period=1)
def eoxdata(header,productsid,Edata):

    with tqdm(total=len(productsid), desc="Extracting eox data") as pbar:
        for id in productsid:
            url = f"https://api.cisco.com/supporttools/eox/rest/5/EOXByProductID/1/{id}?responseencoding=json"
            response = requests.get(url, headers=header)
            if response.status_code == 200:
                eox = response.json()["EOXRecord"][0]
                if "EOXError" in eox.keys():
                    if "does not exist" in eox["EOXError"]["ErrorDescription"]:
                        EndOfSaleDate = "N/A"
                        LastDateOfSupport = "N/A"
                        EOXMigrationDetails = "N/A"
                elif "EOXError" not in eox.keys():        
                    EndOfSaleDate =  eox["EndOfSaleDate"]["value"]
                    LastDateOfSupport = eox["LastDateOfSupport"]["value"]
                    EOXMigrationDetails = eox["EOXMigrationDetails"]["MigrationProductId"]
                    pass
                Edata.append({"Productid":id,"EndOfSaleDate":EndOfSaleDate,"LastDateOfSupport":LastDateOfSupport,
                "EOXMigrationDetails":EOXMigrationDetails})
            elif response.status_code != 200:
                errorMessage = "HTTPError:"+str(response.status_code)
                Edata.append({"Productid":id,"EndOfSaleDate":errorMessage,"LastDateOfSupport":errorMessage,
                "EOXMigrationDetails":errorMessage})
            pbar.update(1)

@on_exception(expo,RateLimitException,max_tries=5)
@limits(calls=10,period=1)
def softwaredata(header,productsid,SFdata):

    with tqdm(total=len(productsid), desc="Extracting software data") as pbar:
        for id in productsid:
            url = f"https://api.cisco.com/software/suggestion/v2/suggestions/software/productIds/{id}"
            response = requests.get(url, headers=header)
            if response.status_code == 200:
                software = response.json()["productList"][0]["suggestions"][0]
                if software["isSuggested"] == "Y":
                    RosVersion = software["releaseFormat2"]
                    SreleaseDate = software["releaseDate"]
                    imageName = software["images"][0]["imageName"]
                elif software["isSuggested"] == "N":
                    RosVersion = "Validate"
                    SreleaseDate = "Validate"
                    imageName = "Validate"
                SFdata.append({"Productid":id,"Version":RosVersion,"SoftwareReleaseDate":SreleaseDate,
                "ImageName":imageName})
            elif response.status_code != 200:
                errorMessage = "HTTPError:"+str(response.status_code)
                SFdata.append({"Productid":id,"Version":errorMessage,"SoftwareReleaseDate":errorMessage,
                "ImageName":errorMessage})
            pbar.update(1)

@on_exception(expo,RateLimitException,max_tries=5)
@limits(calls=5,period=1)
def serialdata(header,serialnumbers,Sdata):

    with tqdm(total=len(serialnumbers), desc="Extracting serial data") as pbar:
        for number in serialnumbers:
            url = f"https://api.cisco.com/sn2info/v2/coverage/summary/serial_numbers/{number}" 
            response = requests.get(url, headers=header)
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
                Sdata.append({"Serial":number,"Customer":customer,
                "ContractEndDate":contractEndDate,"IsCovered":isCovered})
            elif response.status_code != 200:
                errorMessage = "HTTPError:"+str(response.status_code)
                Sdata.append({"SerialNumber":number,"Customer":errorMessage,
                "ContractEndDate":errorMessage,"IsCovered":errorMessage})
            pbar.update(1)

@on_exception(expo,RateLimitException,max_tries=5)
@limits(calls=10,period=1)
def productdata(header,productsid,Pdata):

    with tqdm(total=len(productsid), desc="Extracting product data") as pbar:
        for id in productsid:
            url = f"https://api.cisco.com/product/v1/information/product_ids/{id}"
            response = requests.get(url, headers=header)
            if response.status_code == 200:
                product = response.json()["product_list"][0]
                PreleaseDate = product["release_date"]
                productType = product["product_category"]
                productSeries = product["product_subcategory"]
                productName = product["product_name"].replace(" ","%20")
                Pdata.append({"Productid":id,"ProductReleaseDate":PreleaseDate,"ProductType":productType,
                "ProductSeries":productSeries,"ProductName":productName})
            elif response.status_code != 200:
                errorMessage = "HTTPError:"+str(response.status_code)
                Pdata.append({"Productid":id,"ProductReleaseDate":errorMessage,"ProductType":errorMessage,
                "ProductSeries":errorMessage,"ProductName":errorMessage})
            pbar.update(1)

def supportdata(devicesdf,header,supportdict):

    productsid = list(devicesdf["Model"].unique())
    serialnumbers = list(devicesdf["SerialNumber"].unique())

    eoxdata(header,productsid,Edata)
    softwaredata(header,productsid,SFdata)
    serialdata(header,serialnumbers,Sdata)
    productdata(header,productsid,Pdata)
    
    supportdict["eoxdata"] = Edata
    supportdict["softwaredata"] = SFdata
    supportdict["serialdata"] = Sdata 
    supportdict["productdata"] = Pdata