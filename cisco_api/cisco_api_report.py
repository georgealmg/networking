# !/usr/bin/env python3
# v1.0.0

import concurrent.futures, json, os
from datetime import datetime
from devicedata import device_data, sw_list, sw_out, ios, nxos
from getpass import getpass, getuser
from supportapi import supportdata, header, devices, productsid
from bugapi import bugdata, productnames
from pandas import read_csv, ExcelWriter

try:
    os.chdir(f"/mnt/c/Users/{getuser()}/Documents/Python")
except(FileNotFoundError):
    os.chdir(os.getcwd())

def main():
    
    total_sw = len(sw_list.keys())
    tiempo1 = datetime.now()
    tiempo_inicial = tiempo1.strftime("%H:%M:%S")
    print(f"Hora de inicio: {tiempo_inicial}",f"Total de equipos a validar: {str(total_sw)}",sep="\n")

    with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor_ios:
        ejecucion_ios = {executor_ios.submit(device_data,sw,sw_out,ios,nxos): sw for sw in sw_list.keys()}
    for output_ios in concurrent.futures.as_completed(ejecucion_ios):
        output_ios.result()
    
    file4 = open("devicedata.json","w")
    data = json.dumps(sw_list, indent=4)
    file4.write(data)
    file4.close()

    contador_out = len(sw_out)
    tiempo2 = datetime.now()
    tiempo_final = tiempo2.strftime("%H:%M:%S")
    tiempo_ejecucion = tiempo2 - tiempo1
    print(f"Hora de finalizacion: {tiempo_final}", f"Tiempo de ejecucion: {tiempo_ejecucion}", f"Total de equipos validados: {str(total_sw)}",f"Total de equipos fuera: {str(contador_out)}",sep="\n")

if __name__ == "__main__":
    main()

supportdata(devices,header,productsid)
bugdata(header,productnames)

df1 = read_csv("supportdata.csv", encoding='latin1', on_bad_lines="skip")
df2 = read_csv("bugdata.csv", encoding='latin1', on_bad_lines="skip")
writer = ExcelWriter("cisco_api_report.xlsx", engine='xlsxwriter')
df1.to_excel(writer,sheet_name="support_data",index=None,header=True,freeze_panes=(1,0))
df2.to_excel(writer,sheet_name="bug_data",index=None,header=True,freeze_panes=(1,0))
writer.save()