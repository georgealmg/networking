#!/usr/bin/env python3
#v1.0.0

import os, concurrent.futures, openpyxl, sys
from datetime import datetime
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException, SSHException, AuthenticationException

def DC(sw,user,pas,sw_out):
    def respaldos_DC(net_connect):
        hostname = (net_connect.find_prompt())
        respaldos_txt = open(hostname.strip("#")+".txt","+w")
        respaldos_txt.write(net_connect.send_command("show running-config"))
        respaldos_txt.close()
        try:
            net_connect.save_config()
        except(OSError):
            net_connect.save_config(confirm=True,confirm_response="yes\r")
        net_connect.disconnect()
        print(f"Ejecucion finalizada en {hostname}.")
    try:
        net_connect = ConnectHandler(device_type= "cisco_ios_ssh",host= sw,username= user,password= pas, fast_cli= False)
        respaldos_DC(net_connect)
    except(AuthenticationException):
        sys.exit("Por favor ejecute nuevamente el programa ya que introdujo una contraseña erronea.")
    except(NetMikoTimeoutException,SSHException):
        try:
            net_connect = ConnectHandler(device_type= "cisco_ios_telnet",host= sw,username= user,password= pas, fast_cli= False)
            respaldos_DC(net_connect)
        except:
            print(f"Switch con IP: {str(sw)} esta fuera de linea.")
            sw_out.append(sw)

def main():
    windowsuser = os.getlogin()
    os.chdir("C:/Users/"+windowsuser+"/Documents")
    os.chdir("C:/Users/"+windowsuser+"/Documents/Python-Respaldos")
    user = ""
    pas = ""
    sw_dc = []
    sw_out = []
    fp = open("sw_out.txt","+w")
    archivo_excel = openpyxl.load_workbook("Respaldos.xlsx")
    pestaña_excel = archivo_excel["IP"]
    for ip in range(2, 999999):
        valor = pestaña_excel.cell(row=ip, column=1).value
        if valor != None and valor not in sw_dc:
            sw_dc.append(valor)
        elif valor == None:
            break
    total_sw = len(sw_dc)
    tiempo1 = datetime.now()
    tiempo_inicial = tiempo1.strftime("%H:%M:%S")
    print(f"La ejecucion de este programa inicio a las {tiempo_inicial}, se validara un total de {str(total_sw)} switch.")
    
    fecha = datetime.now()
    directorio_fecha = fecha.strftime("%d-%m-%y")
    directorio = "Data_Center"
    try:
        os.mkdir(f"C:/Users/"+windowsuser+"/Documents/Python-Respaldos/{directorio}")
    except(FileExistsError):
        print(f"La carpeta {directorio} ya existe.")
    os.mkdir(f"C:/Users/"+windowsuser+"/Documents/Python-Respaldos/{directorio}/{directorio_fecha}")
    os.chdir(f"C:/Users/"+windowsuser+"/Documents/Python-Respaldos/{directorio}/{directorio_fecha}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor_nx:
        ejecucion_nx = {executor_nx.submit(DC,sw,user,pas,sw_out,directorio,directorio_fecha): sw for sw in sw_dc}
    for output_nx in concurrent.futures.as_completed(ejecucion_nx):
        output_nx.result()

    print(f"Equipos caidos: {sw_out}")
    os.chdir("C:/Users/"+windowsuser+"/Documents/Python-Respaldos")
    fp.write("Equipos caidos:"+"\n")
    for sw in sw_out:
        fp.write(sw+"\n")
    fp.close()
    contador_out = len(sw_out)
    tiempo2 = datetime.now()
    tiempo_final = tiempo2.strftime("%H:%M:%S")
    print(f"La ejecucion de este programa finalizo a las {tiempo_final}, se validaron un total de {str(total_sw)} switch de los cuales {str(contador_out)} estan fuera de linea.")
    tiempo_ejecucion = tiempo2 - tiempo1
    print(f"El tiempo de ejecucion del programa fue de: {tiempo_ejecucion}")

if __name__ == "__main__":
    main()
