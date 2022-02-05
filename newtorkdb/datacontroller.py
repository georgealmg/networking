#!/usr/bin/env python3
#v1.0.0

import concurrent.futures, json, os, pandas
from datetime import datetime
from getpass import getuser, getpass
from l3data import core, l3dict, l3data
from l2data import l2dict, acc, l2data
from dnsdata import dnsdata

# Con este script se ejecutan los script l3, l2 y infoblox, tambien se une toda la data extraida para formar un solo JSON, este luego sera exportado a Excel.

user = input("Username: ")
pas = getpass()

try:
    os.chdir(f"/mnt/c/Users/{getuser()}/Documents/networking")
except(FileNotFoundError):
    os.chdir(os.getcwd())

total_sw = len(core["ios"]) + len(core["nxos"])
tiempo1 = datetime.now()
tiempo_inicial = tiempo1.strftime("%H:%M:%S")
print("L3 DATA",f"Hora de inicio: {tiempo_inicial}",f"Total de equipos a validar: {str(total_sw)}",sep="\n")

l3data(core,l3dict,user,pas)

# tiempo2 = datetime.now()
# tiempo_final = tiempo2.strftime("%H:%M:%S")
# tiempo_ejecucion = tiempo2 - tiempo1
print("L3 DATA", f"Total de equipos: {str(total_sw)}",sep="\n")
# print("L3 DATA",f"Hora de finalizacion: {tiempo_final}", f"Tiempo de ejecucion: {tiempo_ejecucion}", f"Total de equipos: {str(total_sw)}",sep="\n")

def main():

    sw_out = []
    total_sw = len(acc["ios"]) + len(acc["nxos"])
    # tiempo1 = datetime.now()
    # tiempo_inicial = tiempo1.strftime("%H:%M:%S")
    print("L2 DATA", f"Total de equipos a validar: {str(total_sw)}",sep="\n")
    # print("L2 DATA",f"Hora de inicio: {tiempo_inicial}",f"Total de equipos a validar: {str(total_sw)}",sep="\n")

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        ejecucion = {executor.submit(l2data,device,sw_out,user,pas): device for device in acc["ios"]}
    for output in concurrent.futures.as_completed(ejecucion):
            output.result()
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        ejecucion = {executor.submit(l2data,device,sw_out,user,pas): device for device in acc["nxos"]}
    for output in concurrent.futures.as_completed(ejecucion):
            output.result()

    file = open("l2.json","w")
    data = json.dumps(l2dict, indent=4)
    file.write(data)
    file.close()

    contador_out = len(sw_out)
    # tiempo2 = datetime.now()
    # tiempo_final = tiempo2.strftime("%H:%M:%S")
    # tiempo_ejecucion = tiempo2 - tiempo1
    print("L2 DATA", f"Total de equipos: {str(total_sw)}",f"Total de equipos fuera: {str(contador_out)}",sep="\n")
    # print("L2 DATA",f"Hora de finalizacion: {tiempo_final}", f"Tiempo de ejecucion: {tiempo_ejecucion}", f"Total de equipos: {str(total_sw)}",f"Total de equipos fuera: {str(contador_out)}",sep="\n")

if __name__ == "__main__":
    main()

# tiempo1 = datetime.now()
# tiempo_inicial = tiempo1.strftime("%H:%M:%S")
print("DNS DATA",sep="\n")
# print("DNS DATA",f"Hora de inicio: {tiempo_inicial}",sep="\n")

dnsdata(user,pas)

tiempo2 = datetime.now()
tiempo_final = tiempo2.strftime("%H:%M:%S")
tiempo_ejecucion = tiempo2 - tiempo1
print("DNS DATA",sep="\n")
# print("DNS DATA",f"Hora de finalizacion: {tiempo_final}", f"Tiempo de ejecucion: {tiempo_ejecucion}",sep="\n")

def dataorganizer():

    with open("l3.json", 'r') as file:
        l3json = json.loads(file.read())
    with open("l2.json", 'r') as file:
        l2json = json.loads(file.read())
    with open("dns.json", 'r') as file:
        dnsjson = json.loads(file.read())
    entries = {}

    for env in l3json.keys():
        for ip in l3json[env]:
            entries[ip] = {}
            entries[ip]["env"] = env
            entries[ip]["sw"],entries[ip]["swip"] = '--','--'
            entries[ip]["interface"],entries[ip]["mac"] = '--','--'
            entries[ip]["dns"] = '--'
            for hostname in l2json[env].keys():
                for inter in l2json[env][hostname]["interfaces"].keys():
                    for mac in l2json[env][hostname]["interfaces"][inter]:
                        if l3json[env][ip]["mac"] == mac:
                            entries[ip]["sw"] = hostname
                            entries[ip]["swip"]  = l2json[env][hostname]["swip"]
                            entries[ip]["interface"] =  inter
                            entries[ip]["mac"] = mac
                            try:
                                entries[ip]["dns"] = dnsjson[ip]
                            except(KeyError):
                                pass

    file = open("networkdb.json","w")
    data = json.dumps(entries, indent=4)
    file.write(data)
    file.close()
    
dataorganizer()

os.remove("l3.json")
os.remove("l2.json")
os.remove("dns.json")
print("Organizing DATA")
df = pandas.read_json('networkdb.json',orient='index')
df.to_excel(f"networkdb.xlsx",index='--',header=True,freeze_panes=(1,0))
os.remove('networkdb.json')
print(f"Hora de finalizacion: {tiempo_final}", f"Tiempo de ejecucion: {tiempo_ejecucion}",sep="\n")