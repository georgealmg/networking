# !/usr/bin/env python3
# v1.0.4

import concurrent.futures, pandas as pd, os
from bugapi import bugdata, Bdata, productnames
from datetime import datetime
from devicedata import device_data, Ddata, devices, offline, ios, nxos
from getpass import getuser
from supportapi import supportdata, header, supportdict
# from psirtapi import psirtdata, header, os_dict
from sqlalchemy import create_engine
from tqdm import tqdm

try:
    os.chdir(f"/mnt/c/Users/{getuser()}/Documents/ciscoapi")
except(FileNotFoundError):
    os.chdir(os.getcwd())


engine = create_engine("mysql+pymysql://root:pr0gr4m_SQL@172.25.192.1/ciscoapi")

total = len(devices)
tiempo1 = datetime.now()
tiempo_inicial = tiempo1.strftime("%H:%M:%S")
print(f"Hora de inicio: {tiempo_inicial}")

def main():

    with tqdm(total=len(total), desc="Extracting device data") as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor_ios:
            ejecucion_ios = {executor_ios.submit(device_data,sw,offline,ios,nxos): sw for sw in devices}
        for output_ios in concurrent.futures.as_completed(ejecucion_ios):
            output_ios.result()
            pbar.update(1)

if __name__ == "__main__":
    main()

devicesdf = pd.DataFrame(Ddata)
devicesdf.to_sql('devices', con=engine ,index=False ,if_exists="replace")

supportdata(devices,header,supportdict)
eoxdf = pd.DataFrame(supportdict["eoxdata"])
eoxdf.to_sql('eox', con=engine ,index=False ,if_exists="replace")
softwaredf = pd.DataFrame(supportdict["softwaredata"])
softwaredf.to_sql('software', con=engine ,index=False ,if_exists="replace")
serialdf = pd.DataFrame(supportdict["serialdata"])
serialdf.to_sql('serial', con=engine ,index=False ,if_exists="replace")
productdf = pd.DataFrame(supportdict["productdata"])
productdf.to_sql('product', con=engine ,index=False ,if_exists="replace")

bugdata(header,productnames,devicesdf,productdf,Bdata)
bugdf = pd.DataFrame(Bdata)
bugdf.to_sql('bugs', con=engine ,index=False ,if_exists="replace")

# psirtdata(header,os_dict)

# df3 = read_csv("psirtdata.csv", encoding='latin1', on_bad_lines="skip")
# writer = ExcelWriter("cisco_api_report.xlsx", engine='xlsxwriter')
# df3.to_excel(writer,sheet_name="cve_data",index=None,header=True,freeze_panes=(1,0))
# writer.save()

# os.remove("psirtdata.csv")

# contador_out = len(sw_out)
# tiempo2 = datetime.now()
# tiempo_final = tiempo2.strftime("%H:%M:%S")
# tiempo_ejecucion = tiempo2 - tiempo1
# total_off = len(offline)
# print(f"Hora de finalizacion: {tiempo_final}", f"Tiempo de ejecucion: {tiempo_ejecucion}", f"Total de equipos validados: {str(total_sw)}",
# f"Total de equipos fuera: {str(contador_out)}",sep="\n")