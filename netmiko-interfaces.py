#!/usr/bin/env python3
#v1.0.0

import os, getpass, sys, re, concurrent.futures, openpyxl
from datetime import datetime
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException, SSHException, AuthenticationException

def NXOS(sw_n,user,pas,sw_out,fp):
    def puertas_NXOS(net_connect):
        hostname = (net_connect.find_prompt())
        down = net_connect.send_command("show interface status | ex connected | ex disabled |ex  Po | ex mgmt | ex Disponible | ex Vl")
        inter_1 = re.findall(r"Eth\d/[1-9]\W",down)
        inter_2 = re.findall(r"Eth\d/\d\d",down)
        inter_3 = re.findall(r"Eth\d\d\d/\d/[1-9]\W",down)
        inter_4 = re.findall(r"Eth\d\d\d/\d/\d\d",down)
        def last_conn(net_connect):
            last = net_connect.send_command("show interface %s | include Last" % i)
            if "Last link flapped never" in last:
                description = net_connect.send_command("show interface %s description | include /" % i)
                fp.write(hostname+" "+description.strip("\n")+"\n")
        if inter_1 != []:
            for i in inter_1:
                last_conn(net_connect)        
        elif inter_2 != []:
            for i in inter_2:
                last_conn(net_connect)        
        elif inter_3 != []:
            for i in inter_3:
                last_conn(net_connect)        
        elif inter_4 != []:
            for i in inter_4:
                last_conn(net_connect)
        print(f"Ejecucion finalizada en {hostname}.")
        net_connect.disconnect()
    try:
        net_connect = ConnectHandler(device_type= "cisco_nxos_ssh",host= sw_n,username= user,password= pas)
        puertas_NXOS(net_connect)
    except(AuthenticationException):
        sys.exit("Por favor ejecute nuevamente el programa ya que introdujo una contraseña erronea.")
    except(NetMikoTimeoutException,SSHException):
        try:
            net_connect = ConnectHandler(device_type= "cisco_nxos_telnet",host= sw_n,username= user,password= pas, fast_cli= False)
            puertas_NXOS(net_connect)
        except:
            print(f"Switch con IP: {str(sw_n)} esta fuera de linea.")
            sw_out.append(sw_n)
def IOS(sw_i,user,pas,sw_out,fp,sw_lenovo):
    def puertas_IOS(net_connect):
        hostname = (net_connect.find_prompt())
        down = net_connect.send_command("show interfaces status | exclude connected|Po|Disponible|disabled")
        inter_1 = re.findall(r"Eth\d/[1-9]\W",down)
        inter_2 = re.findall(r"Eth\d/\d\d",down)
        inter_3 = re.findall(r"Eth\d\d\d/\d/[1-9]\W",down)
        inter_4 = re.findall(r"Eth\d\d\d/\d/\d\d",down)
        inter_5 = re.findall(r"Gi\d/[1-9]\W",down)
        inter_6 = re.findall(r"Gi\d/\d\d",down)
        inter_7 = re.findall(r"Gi\d/\d/[1-9]\W",down)
        inter_8 = re.findall(r"Gi\d/\d/\d\d",down)
        inter_9 = re.findall(r"Fa\d/[1-9]\W",down)
        inter_10 = re.findall(r"Fa\d/\d\d",down)
        inter_11 = re.findall(r"Fa\d/\d/[1-9]\W",down)
        inter_12 = re.findall(r"Fa\d/\d/\d\d",down)        
        inter_13 = re.findall(r"Te\d/[1-9]\W",down)
        inter_14 = re.findall(r"Te\d/\d\d",down)
        inter_15 = re.findall(r"Te\d/\d/[1-9]\W",down)
        inter_16 = re.findall(r"Te\d/\d/\d\d",down)
        def last_conn(net_connect):
            last = net_connect.send_command("show interface %s | include Last" % i)
            if "Last link flapped never" in last:
                description = net_connect.send_command("show interface %s description | include /" % i)
                fp.write(hostname+" "+description.strip("\n")+"\n")
            elif "y" in last or "Last input never, output never" in last:
                description = net_connect.send_command("show interface %s description | include /" % i)
                fp.write(hostname+" "+description.strip("\n")+"\n")
        if inter_1 != []:
            for i in inter_1:
                last_conn(net_connect)        
        elif inter_2 != []:
            for i in inter_2:
                last_conn(net_connect)        
        elif inter_3 != []:
            for i in inter_3:
                last_conn(net_connect)        
        elif inter_4 != []:
            for i in inter_4:
                last_conn(net_connect)
        elif inter_5 != []:
            for i in inter_5:
                last_conn(net_connect)        
        elif inter_6 != []:
            for i in inter_6:
                last_conn(net_connect)        
        elif inter_7 != []:
            for i in inter_7:
                last_conn(net_connect)        
        elif inter_8 != []:
            for i in inter_8:
                last_conn(net_connect)
        elif inter_9 != []:
            for i in inter_9:
                last_conn(net_connect)        
        elif inter_10 != []:
            for i in inter_10:
                last_conn(net_connect)        
        elif inter_11 != []:
            for i in inter_11:
                last_conn(net_connect)        
        elif inter_12 != []:
            for i in inter_12:
                last_conn(net_connect)
        elif inter_13 != []:
            for i in inter_13:
                last_conn(net_connect)        
        elif inter_14 != []:
            for i in inter_14:
                last_conn(net_connect)        
        elif inter_15 != []:
            for i in inter_15:
                last_conn(net_connect)        
        elif inter_16 != []:
            for i in inter_16:
                last_conn(net_connect)
        print(f"Ejecucion finalizada en {hostname}.")
        net_connect.disconnect()
    try:
        net_connect = ConnectHandler(device_type= "cisco_ios_ssh",host= sw_i,username= user,password= pas)
        puertas_IOS(net_connect)
    except(AuthenticationException):
        print(f"Error de autenticacion en IP: {sw_i}.")
    except(NetMikoTimeoutException,SSHException):
        try:
            net_connect = ConnectHandler(device_type= "cisco_ios_telnet",host= sw_i,username= user,password= pas, fast_cli= False)
            puertas_IOS(net_connect)
        except:
            print(f"Switch con IP: {str(sw_i)} esta fuera de linea.")
            sw_out.append(sw_i)

def main():
    windowsuser = os.getlogin()
    os.chdir("C:/Users/"+str(windowsuser)+"/Documents")
    user = input("Username: ")
    pas = getpass.getpass()
    sw_nx = []
    sw_ios = []
    sw_out = []
    fp = open("Puertas-DC-down.txt", "w+")
    archivo_excel = openpyxl.load_workbook("Recursos Telco.xlsx")
    pestaña_excel = archivo_excel["Puertas sucursales"]
    for x in range(2, 999999):
        valor = pestaña_excel.cell(row=x, column=2).value
        if valor != None and valor not in sw_ios:
            sw_ios.append(valor)
        elif valor == None:
            break
    for x in range(2, 999999):
        valor = pestaña_excel.cell(row=x, column=3).value
        if valor != None and valor not in sw_nx:
            sw_nx.append(valor)
        elif valor == None:
            break
    total_sw = len(sw_nx) + len(sw_ios)
    tiempo1 = datetime.now()
    tiempo_inicial = tiempo1.strftime("%H:%M:%S")
    print(f"La ejecucion de este programa inicio a las {tiempo_inicial}, se validara un total de {str(total_sw)} switch.")

    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor_nx:
        ejecucion_nx = {executor_nx.submit(NXOS,sw_n,user,pas,sw_out,fp): sw_n for sw_n in sw_nx}
    for output_nx in concurrent.futures.as_completed(ejecucion_nx):
        output_nx.result()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor_ios:
        ejecucion_ios = {executor_ios.submit(IOS,sw_i,user,pas,sw_out,fp): sw_i for sw_i in sw_ios}
    for output_ios in concurrent.futures.as_completed(ejecucion_ios):
        output_ios.result()

    print(f"Equipos caidos: {sw_out}")
    fp.write("Equipos caidos:"+"\n"+str(sw_out))
    fp.close()
    contador_out = len(sw_out)
    tiempo2 = datetime.now()
    tiempo_final = tiempo2.strftime("%H:%M:%S")
    print(f"La ejecucion de este programa finalizo a las {tiempo_final}, se validaron un total de {str(total_sw)} switch de los cuales {str(contador_out)} estan fuera de linea.")
    tiempo_ejecucion = tiempo2 - tiempo1
    print(f"El tiempo de ejecucion del programa fue de: {tiempo_ejecucion}")

if __name__ == "__main__":
    main()
