#!/usr/bin/env python3
#v1.0.2

import concurrent.futures, csv, os, socket
from getpass import getpass, getuser
from datetime import datetime
from napalm import get_network_driver
from netmiko.ssh_exception import NetmikoTimeoutException, SSHException, AuthenticationException
from napalm.base.exceptions import ConnectionException

try:
    os.chdir(f"/mnt/c/Users/{getuser()}/Documents")
except(FileNotFoundError):
    os.chdir(os.getcwd())
        
user = input("Username: ")
pas = getpass()
sw_list = {}
ios = []
nxos = []
sw_out = []
swout_file = open("sw_out.txt","w")
swout_file.close()

total_sw = len(sw_list.keys())
tiempo1 = datetime.now()
tiempo_inicial = tiempo1.strftime("%H:%M:%S")
print(f"Hora de inicio: {tiempo_inicial}",f"Total de equipos a validar: {str(total_sw)}",sep="\n")

data_file = open("descripciones.csv","w", newline='')
first_row = ["Hostname","IP","Interface","State","Description"]
writer = csv.DictWriter(data_file, fieldnames=first_row,dialect="excel")
writer.writeheader()


def descriptions(conn,sw,writer):
    conn.open()
    hostname = conn.get_facts()["hostname"]
    interfaces = conn.get_interfaces()
    for inter in interfaces.keys():
        writer.writerow({"Hostname":hostname ,"IP":sw ,"Interface":inter ,"State":interfaces[inter]["is_up"], "Description":interfaces[inter]["description"]})
    print(f"Validacion finalizada --> {hostname}")
    conn.close()

def connection(sw):
    try:
        if sw in ios:
            driver = get_network_driver("ios")
        elif sw  in nxos:
            driver = get_network_driver("nxos_ssh")
        conn = driver(hostname= sw,username= user, password= pas)
        descriptions(conn,sw,writer)
    except(ConnectionRefusedError, ConnectionResetError):
        sw_out.append(sw)
        print(f"Error:{sw}:ConnectionRefused error")
        swout_file = open("sw_out.txt","a")
        swout_file.write(f"Error:{sw}:ConnectionRefused error"+"\n")
        swout_file.close()
    except(TimeoutError, socket.timeout):
        sw_out.append(sw)
        print(f"Error:{sw}:Timeout error")
        swout_file = open("sw_out.txt","a")
        swout_file.write(f"Error:{sw}:Timeout error"+"\n")
        swout_file.close()
    except(AuthenticationException):
        sw_out.append(sw)
        print(f"Error:{sw}:Authentication error")
        swout_file = open("sw_out.txt","a")
        swout_file.write(f"Error:{sw}:Authentication error"+"\n")
        swout_file.close()
    except(ConnectionException, SSHException, NetmikoTimeoutException):
        try:
            conn = driver(hostname= sw,username= user, password= pas, optional_args= {"transport": 'telnet'})
            driver = get_network_driver("ios")
            descriptions(conn,sw,writer)
        except(ConnectionRefusedError, ConnectionResetError):
            sw_out.append(sw)
            print(f"Error:{sw}:ConnectionRefused error")
            swout_file = open("sw_out.txt","a")
            swout_file.write(f"Error:{sw}:ConnectionRefused error"+"\n")
            swout_file.close()
        except(TimeoutError, socket.timeout):
            sw_out.append(sw)
            print(f"Error:{sw}:Timeout error")
            swout_file = open("sw_out.txt","a")
            swout_file.write(f"Error:{sw}:Timeout error"+"\n")
            swout_file.close()
        except(AuthenticationException):
            sw_out.append(sw)
            print(f"Error:{sw}:Authentication error")
            swout_file = open("sw_out.txt","a")
            swout_file.write(f"Error:{sw}:Authentication error"+"\n")
            swout_file.close()
    except(EOFError):
        sw_out.append(sw)
        print(f"Error:{sw}:EOF error")
        swout_file = open("sw_out.txt","a")
        swout_file.write(f"Error:{sw}:EOF error"+"\n")
        swout_file.close()

def main():

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        ejecucion = {executor.submit(connection,sw): sw for sw in sw_list.keys()}
    for output in concurrent.futures.as_completed(ejecucion):
        output.result()
    data_file.close()

if __name__ == "__main__":
    main()

contador_out = len(sw_out)
tiempo2 = datetime.now()
tiempo_final = tiempo2.strftime("%H:%M:%S")
tiempo_ejecucion = tiempo2 - tiempo1
print(f"Hora de finalizacion: {tiempo_final}", f"Tiempo de ejecucion: {tiempo_ejecucion}", f"Total de equipos validados: {str(total_sw)}"
,f"Total de equipos fuera: {str(contador_out)}",sep="\n")