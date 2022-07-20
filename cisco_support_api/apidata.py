# !/usr/bin/env python3
# v1.0.6

import pandas as pd, os
from bugapi import bugdata, Bdata, productnames
from datetime import datetime
from devicedata import device_data, Ddata, devices, ios, nxos, offline, offline_file
from getpass import getuser
from supportapi import supportdata, header, supportdict
from psirtapi import psirtdata, header, osdict, OSdata
from sqlalchemy import create_engine

try:
    os.chdir(f"/mnt/c/Users/{getuser()}/Documents/cisco_support_api")
except(FileNotFoundError):
    os.chdir(os.getcwd())

engine = create_engine("mysql+pymysql://root:pr0gr4m@172.31.192.1/ciscoapi")

total = len(devices)
tiempo1 = datetime.now()
tiempo_inicial = tiempo1.strftime("%H:%M:%S")
print(f"Hora de inicio: {tiempo_inicial}")

device_data(devices,ios,nxos,offline,offline_file)
devicesdf = pd.DataFrame(Ddata)
devicesdf.to_sql('devices', con=engine ,index=False ,if_exists="replace")

supportdata(devicesdf,header,supportdict)
eoxdf = pd.DataFrame(supportdict["eoxdata"])
eoxdf.to_sql('eox', con=engine ,index=False ,if_exists="replace")
softwaredf = pd.DataFrame(supportdict["softwaredata"])
softwaredf.to_sql('software', con=engine ,index=False ,if_exists="replace")
serialdf = pd.DataFrame(supportdict["serialdata"])
serialdf.to_sql('serialnumbers', con=engine ,index=False ,if_exists="replace")
productdf = pd.DataFrame(supportdict["productdata"])
productdf.to_sql('products', con=engine ,index=False ,if_exists="replace")

bugdata(devicesdf,header,productnames,productdf,Bdata)
bugdf = pd.DataFrame(Bdata)
bugdf.to_sql('bugs', con=engine ,index=False ,if_exists="replace")

psirtdata(devicesdf,header,osdict,OSdata)
psirtdf = pd.DataFrame(OSdata)
psirtdf.to_sql('psirt', con=engine ,index=False ,if_exists="replace")

total_out = len(offline)
tiempo2 = datetime.now()
tiempo_final = tiempo2.strftime("%H:%M:%S")
tiempo_ejecucion = tiempo2 - tiempo1
total_off = len(offline)
print(f"Hora de finalizacion: {tiempo_final}", f"Tiempo de ejecucion: {tiempo_ejecucion}", f"Total de equipos validados: {str(total)-str(total_out)}",
f"Total de equipos fuera: {str(total_out)}",sep="\n")