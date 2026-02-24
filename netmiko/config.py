#!/usr/bin/env python3

import csv, concurrent.futures, os, socket, sys
from dotenv import load_dotenv
from getpass import getuser
from datetime import datetime
from netmiko import ConnectHandler
from netmiko.exceptions import SSHException, AuthenticationException, NetmikoTimeoutException, ReadException
from tqdm import tqdm

try:
    os.chdir(f"C:/Users/{getuser()}/Documents")
except(FileNotFoundError):
    os.chdir(os.getcwd())

load_dotenv("credentials.env")
user = os.environ["user"]
password = os.environ["sdn_pass"]
configc,devices,offline,rows = [],[],[],[]
for ip in open("IP_validacion.txt","r"):
    devices.append(ip.strip("\n"))
outputFile = open("output_config.txt","w")
outputFile.close()
swout = open("result.csv","w", newline='')
first_row = ["IP","Comment"]
writer = csv.DictWriter(swout, fieldnames=first_row)
writer.writeheader()

choice = input("Por favor indicar si los dispositivos cuentan con IOS o NXOS: ")
choice = choice.lower()
quantity = input("Indicar cantidad de comandos: ")
commands = []
print("Introducir comando, uno por linea")
for x in range (0,int(quantity)):
    command = input()
    commands.append(command)

def config(device,conn,configc):
    output = conn.send_config_set(commands, read_timeout=120, terminator=conn.find_prompt())
    output_file = open("output_config.txt","a")
    output_file.write(output+"\n")
    output_file.close()
    conn.save_config()
    configc.append(device)
    if "Invalid" not in output:
        rows.append({"IP":device,"Comment":"Configured"})
    elif "Invalid" in output:
        rows.append({"IP":device,"Comment":"ConfigError"})
    conn.disconnect()

def connection(device,pbar):
    try:
        if choice ==  "ios":
            conn = ConnectHandler(device_type="cisco_ios_ssh", host=device, username=user, password=password, fast_cli=False,
            read_timeout_override=180)
        elif choice == "nxos":
            conn = ConnectHandler(device_type= "cisco_nxos_ssh", host= device, username= user, password=password, fast_cli=False,
            read_timeout_override=180)
        else:
            sys.exit("Favor indicar sistema operativo de los equipos")
        config(device,conn,configc)
    except(ConnectionRefusedError, ConnectionResetError):
        rows.append({"IP":device,"Comment":"ConnectionRefused"})
    except(AuthenticationException):
        rows.append({"IP":device,"Comment":"Authentication"})
    except(TimeoutError, socket.timeout):
        rows.append({"IP":device,"Comment":"Timeout"})
    except(SSHException, NetmikoTimeoutException):
        try:
            conn = ConnectHandler(device_type= "cisco_ios_telnet", host=device, username=user, password=password, fast_cli=False,
            read_timeout_override=180)
            config(device,conn,configc)
        except(ConnectionRefusedError, ConnectionResetError):
            rows.append({"IP":device,"Comment":"ConnectionRefused"})
        except(AuthenticationException):
            rows.append({"IP":device,"Comment":"Authentication"})
        except(TimeoutError, socket.timeout, NetmikoTimeoutException):
            rows.append({"IP":device,"Comment":"Timeout"})
        except(ReadException):
            rows.append({"IP":device,"Comment":"Read"})
    except(ReadException):
        rows.append({"IP":device,"Comment":"Read"})
    except(EOFError):
        rows.append({"IP":device,"Comment":"EOF"})
    
    pbar.update(1)

tiempo1 = datetime.now()
tiempo_inicial = tiempo1.strftime("%H:%M:%S")
print(f"Hora de inicio: {tiempo_inicial}", f"Total de equipos a configurar: {str(len(devices))}", sep="\n")

with tqdm(total=len(devices),desc="Configuring devices",colour="Blue") as pbar:
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        ejecucion = {executor.submit(connection,device,pbar): device for device in devices}
    for output in concurrent.futures.as_completed(ejecucion):
        output.result()

tiempo2 = datetime.now()
tiempo_final = tiempo2.strftime("%H:%M:%S")
tiempo_ejecucion = tiempo2 - tiempo1
print(f"Hora de finalizacion: {tiempo_final}", 
f"Tiempo de ejecucion: {tiempo_ejecucion}", 
f"Total de equipos: {str(len(devices))}",
f"Total de equipos configurados: {str(len(configc))}",
f"Total de equipos fuera: {str(len(devices)-len(configc))}", sep="\n")

writer.writerows(rows)
swout.close()
