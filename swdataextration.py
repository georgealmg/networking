#!/usr/bin/env python3
#v1.0.9

import concurrent.futures, csv, os, re, socket
from datetime import datetime
from getpass import getpass, getuser
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
sw_list = []
nxos = []
ios = []
sw_out = []
swout_file = open("sw_out.txt","w")
swout_file.close()

tiempo1 = datetime.now()
tiempo_inicial = tiempo1.strftime("%H:%M:%S")
total_sw = len(sw_list)
print(f"Hora de inicio: {tiempo_inicial}",f"Total de equipos a validar: {str(total_sw)}",sep="\n")

data_file = open("SWdata.csv","w", newline='')
first_row = ["Hostname","Hostaddress","Port","Description","Status","Duplex","Speed","SFP","VLAN","Mode","Channel","MAC","Config"]
writer = csv.DictWriter(data_file, fieldnames=first_row)
writer.writeheader()

def swdata(conn,sw,ios,nxos,writer):
    hostname = conn.find_prompt()
    print(f"Validacion iniciada --> {hostname}.")
    uplinks = []
    description_dict = {}
    if sw in ios:
        interstatus = parse_output(platform="cisco_ios",command="show interface status",data=conn.send_command("show interface status"))
        channels = parse_output(platform="cisco_ios",command="show etherchannel summary",data=conn.send_command("show etherchannel summary"))
        interdescription = parse_output(platform="cisco_ios",command="show interface description",data=conn.send_command("show interface description"))
        cdp = parse_output(platform="cisco_ios",command="show cdp neighbors",data=conn.send_command("show cdp neighbors"))
    elif sw in nxos:
        interstatus = parse_output(platform="cisco_nxos",command="show interface status",data=conn.send_command("show interface status"))
        channels = parse_output(platform="cisco_nxos",command="show port-channel summary",data=conn.send_command("show port-channel summary"))
        interdescription = parse_output(platform="cisco_nxos",command="show interface description",data=conn.send_command("show interface description"))
        cdp = parse_output(platform="cisco_nxos",command="show cdp neighbors",data=conn.send_command("show cdp neighbors"))
    for interface in interdescription:
        if sw  in ios:
            description_dict[interface["port"]] = interface["descrip"]
        elif sw in nxos:
            description_dict[interface["port"]] = interface["description"]
    for interface in cdp:
        if "H" not in interface["capability"]:
            if "Fas" in interface["local_interface"]:
                uplink = interface["local_interface"].replace("Fas ","Fa")
            elif "Gig" in interface["local_interface"]:
                uplink = interface["local_interface"].replace("Gig ","Gi")
            elif "Ten" in interface["local_interface"]:
                uplink = interface["local_interface"].replace("Ten ","Te")
            elif "Eth" in interface["local_interface"]:
                uplink = interface["local_interface"].replace("Eth ","Eth")
            else:
                pass
            try:
                uplinks.append(uplink)
            except(UnboundLocalError):
                pass
        elif "H" in interface["capability"]:
            pass
    for interface in interstatus:
        if "Vlan" not in interface["port"]:
            port = interface["port"]
            config = conn.send_command(f"show running-config interface {port}")
            if port not in interdescription:
                description_dict[interface["port"]] = interface["name"]
            status = interface["status"]
            duplex = interface["duplex"]
            speed = interface["speed"]
            sfp = interface["type"]
            if interface["vlan"] != "trunk":
                vlan = interface["vlan"]
                mode = "access"
            elif interface["vlan"] == "trunk":
                mode = "trunk"
                trunkconfig = conn.send_command(f"show running-config interface {port} | in allowed")
                if "authorization failed" in trunkconfig:
                    vlan = "Error de autorización"
                else:
                    vlan = re.findall(r"\d+", trunkconfig)
                    if vlan == []:
                        vlan = "Trunk abierto"
            if sw in ios:
                for entry in channels:
                    if port in entry["interfaces"]:
                        channel = entry["po_name"] + "-" + entry["protocol"]
                        if port in uplinks:
                            uplinks.append(entry["po_name"])
                    elif "Po" in port and port == entry["po_name"]:
                        channel = entry["protocol"]
            elif sw in nxos:
                for entry in channels:
                    if port in entry["phys_iface"]:
                        channel = entry["bundle_iface"] + "-" + entry["bundle_proto"]
                        if port in uplinks:
                            uplinks.append(entry["bundle_iface"])
                    elif "Po" in port and port == entry["bundle_iface"]:
                        channel = entry["bundle_proto"]
            if port in uplinks:
                mac = "Interconexion"
            elif port not in uplinks:
                mac_add = conn.send_command(f"show mac address interface {port}")
                if "authorization failed" in mac_add:
                    mac = "Error de autorización"
                else:
                    mac_int = re.findall(r"\w+[.]\w+[.]\w*", mac_add)
                    if mac_int == []:
                        mac = "Interfaz sin MAC"
                    elif mac_int != []:
                        mac = mac_int
        elif "Vlan" in interface["port"]:
            pass
        try:
            writer.writerow({"Hostname":hostname,"Hostaddress":sw,"Port":port,"Description":description_dict[port],"Status":status,"Duplex":duplex,"Speed":speed
        ,"SFP":sfp,"VLAN":vlan,"Mode":mode,"Channel":channel,"MAC":mac,"Config":str(config)})
            del channel
        except(UnboundLocalError):
            channel = "Standalone"
            writer.writerow({"Hostname":hostname,"Hostaddress":sw,"Port":port,"Description":description_dict[port],"Status":status,"Duplex":duplex,"Speed":speed
        ,"SFP":sfp,"VLAN":vlan,"Mode":mode,"Channel":channel,"MAC":mac,"Config":str(config)})
    print(f"Validacion finalizada --> {hostname}.")
    conn.disconnect()

def connection(sw,ios,nxos,writer):
    try:
        if sw in ios:
            conn = ConnectHandler(device_type= "cisco_ios_ssh",host= sw,username= user,password= pas, fast_cli= False)
        elif sw in nxos:
            conn = ConnectHandler(device_type= "cisco_nxos_ssh",host= sw,username= user,password= pas, fast_cli= False)
        swdata(conn,sw,ios,nxos,writer)
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
            swdata(conn,sw,ios,nxos,writer)
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
        ejecucion = {executor.submit(connection,sw,ios,nxos,writer): sw for sw in sw_list}
    for output in concurrent.futures.as_completed(ejecucion):
            output.result()
    data_file.close()

if __name__ == "__main__":
    main()

csv_file = read_csv("swdata.csv", encoding='latin1', on_bad_lines="skip")
csv_file.to_excel(f"swdata.xlsx",index=None,header=True,freeze_panes=(1,0))
os.remove("swdata.csv")

contador_out = len(sw_out)
tiempo2 = datetime.now()
tiempo_final = tiempo2.strftime("%H:%M:%S")
tiempo_ejecucion = tiempo2 - tiempo1
print(f"Hora de finalizacion: {tiempo_final}", f"Tiempo de ejecucion: {tiempo_ejecucion}", f"Total de equipos validados: {str(total_sw)}",
f"Total de equipos fuera: {str(contador_out)}",sep="\n")