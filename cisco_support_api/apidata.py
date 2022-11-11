# !/usr/bin/env python3

# DROP network modules data

import pandas as pd, os, sqlalchemy as db
from acidevices import acidata, apics, ACIdata
from bugapi import bugdata, Bdata, products
from datetime import datetime
from dnacdevices import dnacdata, DNACdata
from dotenv import load_dotenv
from devicedata import device_data, Ddata, offline, offline_file
from getpass import getuser
from genie.testbed import load
from sqlalchemy.exc import ProgrammingError as alchemyerror
from pymysql.err import ProgrammingError as mysqlerror
from netifaces import gateways
from sdwandevices import sdwdata, SDWdata
from supportapi import supportdata, supportdict
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
device_data(devices,offline,offline_file,tb)
standalonedf = pd.DataFrame(Ddata)
standalonedf["OS"] = standalonedf["OS"].replace(to_replace={"IOS":"ios","IOS-XE":"iosxe","NX-OS":"nxos"})
standalonedf["ProductID"] = standalonedf["ProductID"].replace(regex={r"Nexus9\d+\s":"N9K-",r"Nexus7\d+\s":"N7K-",r"Nexus5\d+\s":"N5K-",
"1841":"CISCO1841","2851":"CISCO2851","2801":"CISCO2801","2811":"CISCO2811","3825":"CISCO3825"})

acidata(env_vars,apics,ACIdata)
acidf = pd.DataFrame(ACIdata)
dnacdata(env_vars,DNACdata)
dnacdf = pd.DataFrame(DNACdata)
dnacdf["OS"] = dnacdf["OS"].replace(to_replace={"IOS-XE":"iosxe"})
sdwdata(env_vars,SDWdata)
sdwdf = pd.DataFrame(SDWdata)

devicesdf = pd.concat([standalonedf,acidf,dnacdf,sdwdf])
devicesdf.to_sql('devices', con=engine ,index=False ,if_exists="append")

# devicesdf = pd.read_sql("select * from devices",con=conn)
errors = []
supportdata(env_vars,devicesdf,supportdict,errors)
serialdf = pd.DataFrame(supportdict["serialdata"])
serialdf["SerialNumber"] = serialdf["SerialNumber"].str.strip(" ")
serialdf.to_sql('serialnumbers', con=engine ,index=False ,if_exists="replace")
eoxdf = pd.DataFrame(supportdict["eoxdata"])
eoxdf["ProductID"] = eoxdf["ProductID"].str.strip(" ")
eoxdf.to_sql('eox', con=engine ,index=False ,if_exists="replace")
productdf = pd.DataFrame(supportdict["productdata"])
productdf["ProductID"] = productdf["ProductID"].str.strip(" ")
productdf.to_sql('products', con=engine ,index=False ,if_exists="replace")
softwaredf = pd.DataFrame(supportdict["softwaredata"])
softwaredf["ProductID"] = softwaredf["ProductID"].str.strip(" ")
softwaredf.to_sql('software', con=engine ,index=False ,if_exists="replace")

# productdf = pd.read_sql("select * from products",con=conn)
bugdata(env_vars,devicesdf,products,productdf,Bdata,errors)
bugdf = pd.DataFrame(Bdata)
bugdf["Status"] = bugdf["Status"].replace(to_replace={"O":"Open","F":"Fixed","T":"Terminated"})
bugdf["ProductSeries"] = bugdf["ProductSeries"].replace(regex={r"%20":" "})
bugdf.to_sql('bugs', con=engine ,index=False ,if_exists="replace")

psirtdata(env_vars,devicesdf,osdict,OSdata,errors)
psirtdf = pd.DataFrame(OSdata)
psirtdf.to_sql('psirt', con=engine ,index=False ,if_exists="replace")

errorsdf = pd.DataFrame(errors)
try:
    errorsdf.to_sql('errors', con=engine ,index=False ,if_exists="replace")
except(alchemyerror,mysqlerror,TypeError):
    pass

conn.close()
tiempo2 = datetime.now()
tiempo_final = tiempo2.strftime("%H:%M:%S")
tiempo_ejecucion = tiempo2 - tiempo1
print(f"Hora de finalizacion: {tiempo_final}", f"Tiempo de ejecucion: {tiempo_ejecucion}",sep="\n")