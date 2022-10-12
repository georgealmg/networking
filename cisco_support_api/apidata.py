# !/usr/bin/env python3
# v1.0.11

import pandas as pd, os, sqlalchemy as db
from acidevices import acidata, apics, ACIdata
from bugapi import bugdata, Bdata, products
from datetime import datetime
from dnacdevices import dnacdata, DNACdata
from dotenv import load_dotenv
from devicedata import device_data, Ddata, offline, offline_file
from getpass import getuser
from genie.testbed import load
from netifaces import gateways
from sdwandevices import sdwdata, SDWdata
from supportapi import supportdata, supportdict, productsid
from psirtapi import psirtdata, osdict, OSdata

try:
    os.chdir(f"/mnt/c/Users/{getuser()}/Documents/networking/cisco_support_api")
except(FileNotFoundError):
    os.chdir(os.getcwd())

load_dotenv("cisco_api_variable.env")
env_vars = {}
env_vars["user"] = os.environ["user"]
env_vars["sdn_pass"] = os.environ["sdn_pass"]
env_vars["client_id"] = os.environ["client_id"]
env_vars["client_secret"] = os.environ["client_secret"]
env_vars["dnac"]  = os.environ["dnac"]
env_vars["vmanage"] = os.environ["vmanage"]
env_vars["apic1"] = os.environ["apic1"]
gateway = gateways()["default"][2][0]
engine = db.create_engine(f"mysql+pymysql://root:pr0gr4m@{gateway}/ciscoapi")
conn = engine.connect()

tiempo1 = datetime.now()
tiempo_inicial = tiempo1.strftime("%H:%M:%S")
print(f"Hora de inicio: {tiempo_inicial}")

tb = load('devices.yml')
devices = [""]
total = len(devices)
device_data(devices,offline,offline_file,tb)
devicesdf = pd.DataFrame(Ddata)
devicesdf["OS"] = devicesdf["OS"].replace(to_replace={"IOS":"ios","IOS-XE":"iosxe","NX-OS":"nxos"})
# devicesdf["Model"] = devicesdf["Model"].replace(regex={r"Nexus9\d+\s":"N9K-",r"Nexus7\d+\s":"N7K-",r"Nexus5\d+\s":"N5K-"})

acidata(env_vars,apics,ACIdata)
acidf = pd.DataFrame(ACIdata)
acidf.to_sql('devices', con=engine ,index=False ,if_exists="append")

dnacdata(env_vars,DNACdata)
dnacdf = pd.DataFrame(DNACdata)
dnacdf["OS"] = devicesdf["OS"].replace(to_replace={"IOS-XE":"iosxe"})
dnacdf.to_sql('devices', con=engine ,index=False ,if_exists="append")

sdwdata(env_vars,SDWdata)
sdwdf = pd.DataFrame(SDWdata)
sdwdf.to_sql('devices', con=engine ,index=False ,if_exists="append")

supportdata(env_vars,devicesdf,supportdict)
eoxdf = pd.DataFrame(supportdict["eoxdata"])
eoxdf.to_sql('eox', con=engine ,index=False ,if_exists="replace")
softwaredf = pd.DataFrame(supportdict["softwaredata"])
softwaredf.to_sql('software', con=engine ,index=False ,if_exists="replace")
serialdf = pd.DataFrame(supportdict["serialdata"])
serialdf.to_sql('serialnumbers', con=engine ,index=False ,if_exists="replace")
productdf = pd.DataFrame(supportdict["productdata"])
productdf.to_sql('products', con=engine ,index=False ,if_exists="replace")

devicesdf["ProductID"] = productsid
devicesdf[devicesdf["Hostname","ProductID","SerialNumber","OS","OSVersion"]]
devicesdf.to_sql('devices', con=engine ,index=False ,if_exists="append")

bugdata(env_vars,devicesdf,products,productdf,Bdata)
bugdf = pd.DataFrame(Bdata)
bugdf["Status"] = bugdf["Status"].replace(to_replace={"O":"Open","F":"Fixed","T":"Terminated"})
bugdf["ProductSeries"] = bugdf["ProductSeries"].replace(regex={r"%20":" "})
bugdf.to_sql('bugs', con=engine ,index=False ,if_exists="replace")

psirtdata(env_vars,devicesdf,osdict,OSdata)
psirtdf = pd.DataFrame(OSdata)
psirtdf.to_sql('psirt', con=engine ,index=False ,if_exists="replace")

conn.close()
total_out = len(offline)
tiempo2 = datetime.now()
tiempo_final = tiempo2.strftime("%H:%M:%S")
tiempo_ejecucion = tiempo2 - tiempo1
print(f"Hora de finalizacion: {tiempo_final}", f"Tiempo de ejecucion: {tiempo_ejecucion}", 
f"Total de equipos validados: {str(total-total_out)}",
f"Total de equipos fuera: {str(total_out)}",sep="\n")