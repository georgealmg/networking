#!/usr/bin/env python3
#v1.0.0

import csv, json, requests
from ratelimit import RateLimitException, limits
from backoff import on_exception, expo
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

url = "https://cloudsso.cisco.com/as/token.oauth2"
response = requests.post(url, verify=False, data={"grant_type": "client_credentials"},
headers = {"Content-Type": "application/x-www-form-urlencoded"},
params = {"client_id": "", "client_secret":""})
token = response.json()["token_type"] + " " + response.json()["access_token"]
header = {"Authorization": token}

file = open("devicedata.json","r")
devicedata = json.loads(file.read())
productsid = []
eox_dict,software_dict,serial_dict,product_dict,devices = {},{},{},{},{}

for entry in devicedata.keys():
    try:
        if devicedata[entry]["model"] not in productsid:
            productsid.append(devicedata[entry]["model"])
            devices[devicedata[entry]["model"]] = devicedata[entry]["serial"]
        elif devicedata[entry]["model"] in productsid:
            pass
    except(KeyError):
        pass

@on_exception(expo,RateLimitException,max_tries=5)
@limits(calls=5,period=1)
def eoxdata(header,productsid):

    for id in productsid:
        url = f"https://api.cisco.com/supporttools/eox/rest/5/EOXByProductID/1/{id}?responseencoding=json"
        response = requests.get(url, headers=header)
        if response.status_code == 200:
            eox = response.json()["EOXRecord"][0]
            if "EOXError" in eox.keys():
                if "does not exist" in eox["EOXError"]["ErrorDescription"]:
                    eox_dict[eox["EOXInputValue"]] = {}
                    eox_dict[eox["EOXInputValue"]]["EndOfSaleDate"] = "N/A"
                    eox_dict[eox["EOXInputValue"]]["LastDateOfSupport"] = "N/A"
                    eox_dict[eox["EOXInputValue"]]["EOXMigrationDetails"] = "N/A"
            elif "EOXError" not in eox.keys():        
                if eox["EOLProductID"] not in eox_dict:
                    eox_dict[eox["EOLProductID"]] = {}
                    eox_dict[eox["EOLProductID"]]["EndOfSaleDate"] =  eox["EndOfSaleDate"]["value"]
                    eox_dict[eox["EOLProductID"]]["LastDateOfSupport"] = eox["LastDateOfSupport"]["value"]
                    eox_dict[eox["EOLProductID"]]["EOXMigrationDetails"] = eox["EOXMigrationDetails"]["MigrationProductId"]
                elif eox["EOLProductID"] in eox_dict:
                    pass
            print(id)
        elif response.status_code != 200:
            print(f"EOX API, HTTP error code {response.status_code}, device model {id}")
    
    data = json.dumps(eox_dict, indent=4)
    file = open("eoxdata.json","w")
    file.write(data)
    file.close()

@on_exception(expo,RateLimitException,max_tries=5)
@limits(calls=10,period=1)
def softwaredata(header,productsid):

    for id in productsid:
        url = f"https://api.cisco.com/software/suggestion/v2/suggestions/software/productIds/{id}"
        response = requests.get(url, headers=header)
        if response.status_code == 200:
            software = response.json()["productList"][0]["suggestions"][0]
            if software["isSuggested"] == "Y":
                software_dict[id] = {}
                software_dict[id]["version"] = software["releaseFormat2"]
                software_dict[id]["releasedate"] = software["releaseDate"]
                software_dict[id]["imageName"] = software["images"][0]["imageName"]
            elif software["isSuggested"] == "N":
                software_dict[id] = {}
                software_dict[id]["version"] = "Validate"
                software_dict[id]["releasedate"] = "Validate"
                software_dict[id]["imageName"] = "Validate"
            print(id)
        elif response.status_code != 200:
            print(f"Software API, HTTP error code {response.status_code}, device model {id}")

    data = json.dumps(software_dict, indent=4)
    file = open("softwaredata.json","w")
    file.write(data)
    file.close()

@on_exception(expo,RateLimitException,max_tries=5)
@limits(calls=5,period=1)
def serialdata(header,devices):

    for id in devices.keys():
        url = f"https://api.cisco.com/sn2info/v2/coverage/summary/serial_numbers/" + devices[id]
        response = requests.get(url, headers=header)
        if response.status_code == 200:
            try:
                serial = response.json()["serial_numbers"][0]
                serial_dict[id] = {}
                serial_dict[id]["customer"] = serial["contract_site_customer_name"]
                serial_dict[id]["end_date"] = serial["covered_product_line_end_date"]
                serial_dict[id]["is_covered"] = serial["is_covered"]
            except(KeyError):
                serial = response.json()
                errordata = json.dumps(serial,indent=4)
                file = open(f"{id}.json","w")
                file.write(errordata)
                file.close()
            print(id)
        elif response.status_code != 200:
            print(f"Serial number API, HTTP error code {response.status_code}, device model {id}")

    data = json.dumps(serial_dict, indent=4)
    file = open("serialdata.json","w")
    file.write(data)
    file.close()

@on_exception(expo,RateLimitException,max_tries=5)
@limits(calls=10,period=1)
def productdata(header,productsid):
        
    for id in productsid:
        if response.status_code == 200:
            url = f"https://api.cisco.com/product/v1/information/product_ids/{id},"
            response = requests.get(url, headers=header)
            product = response.json()["product_list"][0]
            product_dict[id] = {}
            product_dict[id]["release_date"] = product["release_date"]
            product_dict[id]["product_type"] = product["product_category"]
            product_dict[id]["product_series"] = product["product_subcategory"]
            product_dict[id]["product_name"] = product["product_name"].replace(" ","%20")
            print(id)
        elif response.status_code != 200:
            print(f"Product ID API, HTTP error code {response.status_code}, device model {id}")

    data = json.dumps(product_dict, indent=4)
    file = open("productdata.json","w")
    file.write(data)
    file.close()

def supportdata(devices,header,productsid):

    data_file = open("supportdata.csv","w", newline='',encoding="utf-8")
    first_row = ["hostname","ip","serial","product_type","product_series","model","release_date",
    "end_of_sale_date","end_of_support_date","migration_product_id","is_covered_by_contract",
    "customer","end__of_contract_date","os_family","current_os","recommended_os","recommended_os_release_date","os_image_name"]
    writer = csv.DictWriter(data_file, fieldnames=first_row, restval="Error")
    writer.writeheader()

    eoxdata(header,productsid)
    file = open("eoxdata.json","r")
    eox_dict = json.loads(file.read())
    softwaredata(header,productsid)
    file = open("softwaredata.json","r")
    software_dict = json.loads(file.read())
    serialdata(header,devices)
    file = open("serialdata.json","r")
    serial_dict = json.loads(file.read())
    productdata(header,productsid)
    file = open("productdata.json","r")
    product_dict = json.loads(file.read())

    for ip in devicedata.keys():
        if devicedata[ip] != {}:
            hostname = devicedata[ip]["hostname"]
            serial = devicedata[ip]["serial"]
            model = devicedata[ip]["model"]
            current_os = devicedata[ip]["version"]
            os_family = devicedata[ip]["os"]
            try:
                release_date = product_dict[model]["release_date"]
                product_type = product_dict[model]["product_type"]
                product_series = product_dict[model]["product_series"]
            except(KeyError):
                release_date = "no data"
                product_type = "no data"
                product_series = "no data"
            try:
                end_of_sale_date = eox_dict[model]["EndOfSaleDate"]
                end_of_support_date = eox_dict[model]["LastDateOfSupport"]
                migration_product_id = eox_dict[model]["EOXMigrationDetails"]
            except(KeyError):
                end_of_sale_date = "no data"
                end_of_support_date = "no data"
                migration_product_id = "no data"
            try:
                is_covered_by_contract = serial_dict[model]["is_covered"]
                customer = serial_dict[model]["customer"]
                end__of_contract_date = serial_dict[model]["end_date"]
            except(KeyError):
                is_covered_by_contract = "no data"
                customer = "no data"
                end__of_contract_date = "no data"
            try:
                recommended_os = software_dict[model]["version"]
                recommended_os_release_date = software_dict[model]["releasedate"]
                os_image_name = software_dict[model]["imageName"]
            except(KeyError):
                recommended_os = "no data"
                recommended_os_release_date = "no data"
                os_image_name = "no data"
        elif devicedata[ip] == {}:
            hostname = "no data"
            serial = "no data"
            model = "no data"
            current_os = "no data"
            os_family = "no data"
            release_date = "no data"
            product_type = "no data"
            product_series = "no data"
            end_of_sale_date = "no data"
            end_of_support_date = "no data"
            migration_product_id = "no data"
            is_covered_by_contract = "no data"
            customer = "no data"
            end__of_contract_date = "no data"
            recommended_os = "no data"
            recommended_os_release_date = "no data"
            os_image_name = "no data"


        writer.writerow({"hostname":hostname,"ip":ip,"serial":serial,"product_type":product_type,"product_series":product_series,
        "model":model,"release_date":release_date,"end_of_sale_date":end_of_sale_date,"end_of_support_date":end_of_support_date,
        "migration_product_id":migration_product_id,"is_covered_by_contract":is_covered_by_contract,"customer":customer,
        "end__of_contract_date":end__of_contract_date,"os_family":os_family,"current_os":current_os,"recommended_os":recommended_os,
        "recommended_os_release_date":recommended_os_release_date,"os_image_name":os_image_name})

    data_file.close()
supportdata(devices,header,productsid)