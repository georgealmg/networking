#!/usr/bin/env python3
#v1.0.2

import concurrent.futures, os, socket
from getpass import getpass, getuser
from datetime import datetime
from netmiko import ConnectHandler
from netmiko.ssh_exception import SSHException, AuthenticationException
from tqdm import tqdm

try:
    os.chdir(f"/mnt/c/Users/{getuser()}/Documents")
except(FileNotFoundError):
    os.chdir(os.getcwd())

user = input("Username: ")
pas = getpass()
commands = []
devices,offline,configured = [],[],[]
result = open("result.txt","w")
output = open("output.txt","w")
result.close()
output.close()

total = len(devices)
tiempo1 = datetime.now()
tiempo_inicial = tiempo1.strftime("%H:%M:%S")
print(f"Hora de inicio: {tiempo_inicial}",f"Total de equipos a configurar: {str(total)}",sep="\n")

for ip in open("IP_validacion.txt","r"):
    devices.append(ip.strip("\n"))

def config(sw,conn,configured,commands):
    hostname = conn.find_prompt()
    output = conn.send_config_set(commands)
    output = open("output.txt","a")
    output.write(output+"\n")
    output.close()
    conn.save_config()
    configured.append(sw)
    result = open("result.txt","a")
    result.write(f"OK:{sw}:Configurado"+"\n")
    result.close()
    conn.disconnect()

def connection(sw):
    try:
        conn = ConnectHandler(device_type= "cisco_ios_ssh",host= sw,username= user,password= pas)
        config(sw,conn,configured,commands)
    except(ConnectionRefusedError, ConnectionResetError):
        offline.append(sw)
        result = open("result.txt","a")
        result.write(f"Error:{sw}:ConnectionRefused error"+"\n")
        result.close()
    except(TimeoutError, socket.timeout):
        offline.append(sw)
        result = open("result.txt","a")
        result.write(f"Error:{sw}:Timeout error"+"\n")
        result.close()
    except(AuthenticationException):
        offline.append(sw)
        result = open("result.txt","a")
        result.write(f"Error:{sw}:Authenticacion error"+"\n")
        result.close()
    except(SSHException):
        try:
            conn = ConnectHandler(device_type= "cisco_ios_telnet",host= sw,username= user,password= pas)
            config(sw,conn,configured,commands)
        except(ConnectionRefusedError, ConnectionResetError):
            offline.append(sw)
            result = open("result.txt","a")
            result.write(f"Error:{sw}:ConnectionRefused error"+"\n")
            result.close()
        except(TimeoutError, socket.timeout):
            offline.append(sw)
            result = open("result.txt","a")
            result.write(f"Error:{sw}:Timeout error"+"\n")
            result.close()
        except(AuthenticationException):
            offline.append(sw)
            result = open("result.txt","a")
            result.write(f"Error:{sw}:Authenticacion error"+"\n")
            result.close()
    except(EOFError):
        offline.append(sw)
        result = open("result.txt","a")
        result.write(f"Error:{sw}:EOF error"+"\n")
        result.close()

def main():
    with tqdm(total=total,desc="Configuring devices") as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            ejecucion = {executor.submit(connection,sw): sw for sw in devices}
        for output in concurrent.futures.as_completed(ejecucion):
            output.result()
        pbar.update(1)

if __name__ == "__main__":
    main()

contador_out = len(offline)
tiempo2 = datetime.now()
tiempo_final = tiempo2.strftime("%H:%M:%S")
tiempo_ejecucion = tiempo2 - tiempo1
print(f"Hora de finalizacion: {tiempo_final}", f"Tiempo de ejecucion: {tiempo_ejecucion}", f"Total de equipos: {str(total)}",
f"Total de equipos configurados: {str(len(configured))}",f"Total de equipos fuera: {str(contador_out)}",sep="\n")