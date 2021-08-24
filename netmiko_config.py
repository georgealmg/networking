#!/usr/bin/env python3
#v1.0.1

from netmiko import ConnectHandler
from netmiko.ssh_exception import SSHException, AuthenticationException, NetmikoTimeoutException
from datetime import datetime
import getpass, os, sys, concurrent.futures

def NXOS(sw_n,user,pas,fp,fp1,comandos_nx):
    def rutas(conn):
        hostname = conn.find_prompt()
        print(f"Ejecucion iniciada en {hostname} : {sw_n}")
        output = conn.send_config_set(comandos_nx)
        fp.write(f"{hostname} {sw_n}\n{output}\n")
        clock = conn.send_command("show clock")
        run_config = conn.send_command("show running-config")
        fp1.write(f"{hostname} {sw_n}\n{clock}\n{run_config}")
        print(f"Ejecucion finalizada en {hostname} : {sw_n}")
        conn.disconnect()
    try:
        conn = ConnectHandler(device_type= "cisco_nxos_ssh",host= sw_n,username= user,password= pas)
        rutas(conn)
    except(AuthenticationException):
        sys.exit("Por favor ejecute nuevamente el programa ya que introdujo una contraseña erronea.")
    except(SSHException, NetmikoTimeoutException):
        print(f"Switch con IP: {sw_n} esta fuera de linea")

def main():

    windowsuser = os.getlogin()
    os.chdir("C:/Users/"+windowsuser+"/Documents")
    user = input("Username: ")
    pas = getpass.getpass()

    sw_nx = []
    comandos_nx = []
    fp = open("config.txt","w+")
    fp1 = open("respaldos.txt","w+")
    tiempo1 = datetime.now()
    tiempo_inicial = tiempo1.strftime("%H:%M:%S")
    print(f"La ejecucion de este programa inicio a las {tiempo_inicial}, se validara un total de {str(len(sw_nx))} switch.")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor_nx:
        ejecucion_nx = {executor_nx.submit(NXOS,sw_n,user,pas,fp,fp1,comandos_nx,): sw_n for sw_n in sw_nx}
    for output_nx in concurrent.futures.as_completed(ejecucion_nx):
        output_nx.result()

    fp.close()
    fp1.close()
    tiempo2 = datetime.now()
    tiempo_final = tiempo2.strftime("%H:%M:%S")
    print(f"La ejecucion de este programa finalizo a las {tiempo_final}, se validaro un total de {str(len(sw_nx))}")
    tiempo_ejecucion = tiempo2 - tiempo1
    print(f"El tiempo de ejecucion del programa fue de: {tiempo_ejecucion}")

if __name__ == "__main__":
    main()
