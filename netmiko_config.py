#!/usr/bin/env python3
#v1.0.4

import concurrent.futures, os, sys
from getpass import getpass, getuser
from netmiko import ConnectHandler
from netmiko.ssh_exception import SSHException, AuthenticationException, NetmikoTimeoutException
from datetime import datetime

def config(sw,conn,comandos):
    hostname = conn.find_prompt()
    print(f"Ejecucion iniciada --> {hostname}.")
    output = conn.send_config_set(comandos)
    outputfile = open("config.txt","a")
    outputfile.write(f"{hostname} {sw}\n{output}\n")
    outputfile.close()
    print(f"Ejecucion finalizada --> {hostname}.")
    conn.save_config()
    conn.disconnect()

def connection(sw,user,pas,sw_out,comandos):
    try:
        conn = ConnectHandler(device_type= "cisco_ios_ssh",host= sw,username= user,password= pas, fast_cli= False)
        config(sw,conn,comandos)
    except(ConnectionRefusedError):
        sw_out.append(sw)
        print(f"Error:{sw}:ConnectionRefused error")
        swout_file = open("sw_out.txt","a")
        swout_file.write(f"Error:{sw}:ConnectionRefused error"+"\n")
        swout_file.close()
    except(AuthenticationException):
        sw_out.append(sw)
        print(f"Error:{sw}:Authentication error")
        swout_file = open("sw_out.txt","a")
        swout_file.write(f"Error:{sw}:Authentication error"+"\n")
        swout_file.close()
    except(SSHException):
        try:
            conn = ConnectHandler(device_type= "cisco_ios_telnet",host= sw,username= user,password= pas,fast_cli= False)
            config(sw,conn,comandos)
        except(ConnectionRefusedError):
            sw_out.append(sw)
            print(f"Error:{sw}:ConnectionRefused error")
            swout_file = open("sw_out.txt","a")
            swout_file.write(f"Error:{sw}:ConnectionRefused error"+"\n")
            swout_file.close()
        except(TimeoutError):
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
    try:
       os.chdir(f"/mnt/c/Users/{getuser()}/Documents/networking")
    except(FileNotFoundError):
        os.chdir(os.getcwd())
    user = input("Username: ")
    pas = getpass()
    sw_ios = []
    comandos = []
    sw_out = []
    outputfile = open("config.txt","w")
    outputfile.close()
    swout_file = open("sw_out.txt","w")
    swout_file.close()

    tiempo1 = datetime.now()
    tiempo_inicial = tiempo1.strftime("%H:%M:%S")
    print(f"Hora de inicio: {tiempo_inicial}",f"Total de equipos a configurar: {str(len(sw_ios))}",sep="\n")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        ejecucion = {executor.submit(config,sw,user,pas,sw_out,comandos): sw for sw in sw_ios}
    for output in concurrent.futures.as_completed(ejecucion):
        output.result()

    tiempo2 = datetime.now()
    tiempo_final = tiempo2.strftime("%H:%M:%S")
    tiempo_ejecucion = tiempo2 - tiempo1
    print(f"Hora de finalizacion: {tiempo_final}", f"Tiempo de ejecucion: {tiempo_ejecucion}", f"Total de equipos: {str(len(sw_ios))}", 
    f"Total de equipos configurados{str(len(sw_ios) - len(sw_out))}", f"Total de equipos fuera: {str(len(sw_out))}",sep="\n")

if __name__ == "__main__":
    main()
