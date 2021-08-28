#!/usr/bin/env python3
#v1.0.2

from netmiko import ConnectHandler
from netmiko.ssh_exception import SSHException, AuthenticationException, NetmikoTimeoutException
from datetime import datetime
import getpass, os, sys, concurrent.futures

def config(sw,user,pas,fp,fp1,comandos_nx,out_count):
    try:
        conn = ConnectHandler(device_type= "cisco_nxos_ssh",host= sw,username= user,password= pas)
    except(AuthenticationException):
        sys.exit("Por favor ejecute nuevamente el programa ya que introdujo una contraseña erronea.")
    except(SSHException, NetmikoTimeoutException):
        out_count += 1
        fp1.write(sw+"\n")
        print(f"Switch con IP \"{sw}\" esta fuera de linea")
        return None
    hostname = conn.find_prompt()
    print(f"Ejecucion iniciada en {hostname} : {sw}")
    output = conn.send_config_set(comandos_nx)
    fp.write(f"{hostname} {sw}\n{output}\n")
    print(f"Ejecucion finalizada en {hostname} : {sw}")
    conn.save_config()
    conn.disconnect()

def main():
    
    windowsuser = os.getlogin()
    try:
        os.chdir("C:/Users/"+str(windowsuser)+"/Documents")
    except(FileNotFoundError):
        os.chdir(os.getcwd())
    user = input("Username: ")
    pas = getpass.getpass()

    sw_nxos = []
    comandos_nx = []
    out_count = 0
    fp = open("config.txt","w+")
    fp1 = open("sw_out.txt","w+")
    tiempo1 = datetime.now()
    tiempo_inicial = tiempo1.strftime("%H:%M:%S")
    print(f"La ejecucion de este programa inicio a las {tiempo_inicial}, se validara un total de {str(len(sw_nxos))} switch.")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor_nx:
        ejecucion_nx = {executor_nx.submit(config,sw,user,pas,fp,fp1,comandos_nx,out_count): sw for sw in sw_nxos}
    for output_nx in concurrent.futures.as_completed(ejecucion_nx):
        output_nx.result()

    fp.close()
    fp1.close()
    tiempo2 = datetime.now()
    tiempo_final = tiempo2.strftime("%H:%M:%S")
    print(f"La ejecucion de este programa finalizo a las {tiempo_final}, se configurara un total de {str(len(sw_nxos))} equipos")
    tiempo_ejecucion = tiempo2 - tiempo1
    print(f"El tiempo de ejecucion del programa fue de {tiempo_ejecucion}, {str(out_count)} de los equipos no pudieron ser configurados")

if __name__ == "__main__":
    main()
