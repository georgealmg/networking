#!/usr/bin/env python3
#v1.0.1

import concurrent.futures, os, socket
from getpass import getpass, getuser
from datetime import datetime
from netmiko import ConnectHandler
from netmiko.ssh_exception import SSHException, AuthenticationException

try:
    os.chdir("C:/Python")
except(FileNotFoundError):
    try:
        os.chdir(f"/mnt/c/Users/{getuser()}/Documents/Python")
    except(FileNotFoundError):
        os.chdir(os.getcwd())

user = input("Username: ")
pas = getpass()
sw_list = []
sw_out = []
sw_config = []
commands = []
swout_file = open("sw_result.txt","w")
output_file = open("output_config.txt","w")
swout_file.close()
output_file.close()

for ip in open("IP_validacion.txt","r"):
    sw_list.append(ip.strip("\n"))

def config(sw,conn,sw_config,commands):
    hostname = conn.find_prompt()
    print(f"Configuracion iniciada --> {hostname}")
    output = conn.send_config_set(commands)
    output_file = open("output_config.txt","a")
    output_file.write(output+"\n")
    output_file.close()
    conn.save_config()
    sw_config.append(sw)
    swout_file = open("sw_result.txt","a")
    swout_file.write(f"OK:{sw}:Configurado"+"\n")
    swout_file.close()
    print(f"Configuracion finalizada --> {hostname}")
    conn.disconnect()

def connection(sw):
    try:
        conn = ConnectHandler(device_type= "cisco_ios_ssh",host= sw,username= user,password= pas)
        config(sw,conn,sw_config,commands)
    except(ConnectionRefusedError, ConnectionResetError):
        sw_out.append(sw)
        print(f"Error:{sw}:ConnectionRefused error")
        swout_file = open("sw_result.txt","a")
        swout_file.write(f"Error:{sw}:ConnectionRefused error"+"\n")
        swout_file.close()
    except(TimeoutError, socket.timeout):
        sw_out.append(sw)
        print(f"Error:{sw}:Timeout error")
        swout_file = open("sw_result.txt","a")
        swout_file.write(f"Error:{sw}:Timeout error"+"\n")
        swout_file.close()
    except(AuthenticationException):
        sw_out.append(sw)
        print(f"Error:{sw}:Authenticacion error")
        swout_file = open("sw_result.txt","a")
        swout_file.write(f"Error:{sw}:Authenticacion error"+"\n")
        swout_file.close()
    except(SSHException):
        try:
            conn = ConnectHandler(device_type= "cisco_ios_telnet",host= sw,username= user,password= pas)
            config(sw,conn,sw_config,commands)
        except(ConnectionRefusedError, ConnectionResetError):
            sw_out.append(sw)
            print(f"Error:{sw}:ConnectionRefused error")
            swout_file = open("sw_result.txt","a")
            swout_file.write(f"Error:{sw}:ConnectionRefused error"+"\n")
            swout_file.close()
        except(TimeoutError, socket.timeout):
            sw_out.append(sw)
            print(f"Error:{sw}:Timeout error")
            swout_file = open("sw_result.txt","a")
            swout_file.write(f"Error:{sw}:Timeout error"+"\n")
            swout_file.close()
        except(AuthenticationException):
            sw_out.append(sw)
            print(f"Error:{sw}:Authenticacion error")
            swout_file = open("sw_result.txt","a")
            swout_file.write(f"Error:{sw}:Authenticacion error"+"\n")
            swout_file.close()
    except(EOFError):
        sw_out.append(sw)
        print(f"Error:{sw}:EOF error")
        swout_file = open("sw_result.txt","a")
        swout_file.write(f"Error:{sw}:EOF error"+"\n")
        swout_file.close()

def main():

    total_sw = len(sw_list)
    tiempo1 = datetime.now()
    tiempo_inicial = tiempo1.strftime("%H:%M:%S")
    print(f"Hora de inicio: {tiempo_inicial}",f"Total de equipos a validar: {str(total_sw)}",sep="\n")

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        ejecucion = {executor.submit(connection,sw): sw for sw in sw_list}
    for output in concurrent.futures.as_completed(ejecucion):
            output.result()

    contador_out = len(sw_out)
    tiempo2 = datetime.now()
    tiempo_final = tiempo2.strftime("%H:%M:%S")
    tiempo_ejecucion = tiempo2 - tiempo1
    print(f"Hora de finalizacion: {tiempo_final}", f"Tiempo de ejecucion: {tiempo_ejecucion}", f"Total de equipos: {str(total_sw)}",f"Total de equipos configurados: {str(len(sw_config))}",f"Total de equipos fuera: {str(contador_out)}",sep="\n")

if __name__ == "__main__":
    main()