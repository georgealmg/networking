#!/usr/bin/env python3
#v1.1.0

import csv,concurrent.futures, os, socket
from getpass import getpass, getuser
from datetime import datetime
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetmikoTimeoutException, SSHException, AuthenticationException
from ntc_templates.parse import parse_output
from pandas import read_csv

try:
    os.chdir(f"/mnt/c/Users/{getuser()}/Documents")
except(FileNotFoundError):
    os.chdir(os.getcwd())
        
user = input("Username: ")
pas = getpass()
sw_list,sw_out = [],[]
data = {}
swout_file = open("sw_out.txt","w")
swout_file.close()

tiempo1 = datetime.now()
tiempo_inicial = tiempo1.strftime("%H:%M:%S")
total_sw = len(sw_list)
print(f"Hora de inicio: {tiempo_inicial}",f"Total de equipos a validar: {str(total_sw)}",sep="\n")

data_file = open("Ports.csv","w", newline='')
first_row = ["Hostname","Hostaddress","Port","PoE","Status","Description","VLAN"]
writer = csv.DictWriter(data_file, fieldnames=first_row)
writer.writeheader()

def ports(conn,sw):
    hostname = conn.find_prompt()
    data[hostname] = []
    power = conn.send_command("show power inline")
    interface = parse_output(platform="cisco_ios",command="show interface",data=conn.send_command("show interface"))
    inter_status = parse_output(platform="cisco_ios",command="show interface status",data=conn.send_command("show interface status"))
    description = parse_output(platform="cisco_ios",command="show interface description",data=conn.send_command("show interface description"))
    for value in interface:
        if "FastEthernet" in value["interface"] or "GigabitEthernet" in value["interface"]:
            if "up" not in value["protocol_status"] and ((value["last_input"] == "never" and value["last_output"] 
            == "never") or ("y" in value["last_input"] or "y" in value["last_output"])):
                if "FastEthernet" in value["interface"]:
                    port = value["interface"].replace("FastEthernet","Fa")
                elif "GigabitEthernet" in value["interface"]:
                    port = value["interface"].replace("GigabitEthernet","Gi")
                if port in power:
                    poe = "PoE"
                elif port not in power:
                    poe = "No PoE"
                for value in inter_status:
                    if value["port"] == port:
                        vlan = value["vlan"]
                        status = value["status"]
                for value in description:
                    if value["port"] == port:
                        descrip = value["descrip"]
                try:
                    data[hostname].append({"Hostname":hostname,"Hostaddress":sw,"Port":port,"PoE":poe,"Status":status,"Description":descrip,"VLAN":vlan})
                except(UnboundLocalError):
                    pass
        else:
            pass
    print(f"Validacion finalizada --> {hostname}")
    conn.disconnect()

def connection(sw):
    try:
        conn = ConnectHandler(device_type= "cisco_ios_ssh",host= sw,username= user,password= pas, fast_cli= False)
        ports(conn,sw)
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
    except(SSHException, NetmikoTimeoutException):
        try:
            conn = ConnectHandler(device_type= "cisco_ios_telnet",host= sw,username= user,password= pas,fast_cli= False)
            ports(conn,sw)
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

    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
        ejecucion = {executor.submit(connection,sw): sw for sw in sw_list}
    for output in concurrent.futures.as_completed(ejecucion):
            output.result()

if __name__ == "__main__":
    main()

for entry in data.keys():
    rows = data[entry]
    writer.writerows(rows)
data_file.close()

csv_file = read_csv("Ports.csv", encoding='latin1', on_bad_lines="skip")
csv_file.to_excel(f"Ports.xlsx",index=None,header=True,freeze_panes=(1,0))
os.remove("Ports.csv")

contador_out = len(sw_out)
tiempo2 = datetime.now()
tiempo_final = tiempo2.strftime("%H:%M:%S")
tiempo_ejecucion = tiempo2 - tiempo1
print(f"Hora de finalizacion: {tiempo_final}", f"Tiempo de ejecucion: {tiempo_ejecucion}", f"Total de equipos validados: {str(total_sw)}",
f"Total de equipos fuera: {str(contador_out)}",sep="\n")