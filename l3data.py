#!/usr/bin/env python3
#v1.0.0

import json
from netmiko import ConnectHandler
from netmiko.ssh_exception import SSHException, AuthenticationException
from ntc_templates.parse import parse_output

core = {"nxos":[], "ios":[]}
l3dict = {"nxos":[], "ios":[]}
user ,password = None, None

# El objetivo de este script es la extraccion de las tablas ARP de los distintos core de la red.
# Existen dos funciones, una para NXOS y otra para IOS, esto debido a la diferencia en los output de cada OS.
# La data se almacena en un JSON.

def l3data_nxos(core,l3dict):
    for device in core["nxos"]:
        conn = ConnectHandler(device_type="cisco_nxos_ssh" ,host=device ,username=user ,password=password)
        print(f"Extrayendo data l3 --> {conn.find_prompt()}")
        arp = parse_output(platform="cisco_nxos",command="show ip arp",data=conn.send_command(f"show ip arp"))
        for entry in arp:
            if entry["interface"] not in l3dict["nxos"].keys():
                l3dict["nxos"][entry["address"]] = {}
                l3dict["nxos"][entry["address"]]["l3inter"] = entry["interface"]
                l3dict["nxos"][entry["address"]]["mac"] = entry["mac"]
            elif entry["interface"] in l3dict["nxos"].keys():
                pass
        conn.disconnect()

def l3data_ios(core,l3dict):
    for device in core["ios"]:
        conn = ConnectHandler(device_type="cisco_ios_ssh" ,host=device ,username=user ,password=password)
        print(f"Extrayendo data l3 --> {conn.find_prompt()}")
        arp = parse_output(platform="cisco_ios",command="show ip arp",data=conn.send_command(f"show ip arp"))
        for entry in arp:
            if entry["interface"] not in l3dict["ios"].keys():
                l3dict["ios"][entry["address"]] = {}
                l3dict["ios"][entry["address"]]["l3inter"] = entry["interface"]
                l3dict["ios"][entry["address"]]["mac"] = entry["mac"]
            elif entry["interface"] in l3dict["ios"].keys():
                pass
        conn.disconnect()

def l3data(core,l3dict):
    try:
        l3data_nxos(core,l3dict)
        l3data_ios(core,l3dict)
    except(ConnectionRefusedError):
        print(f"Error --> ConnectionRefused error")
    except(AuthenticationException):
        print(f"Error --> Authenticacion error")
    except(SSHException):
        print(f"Error --> ConnectionRefused error")
    except(EOFError):
        print(f"Error --> EOF error")

    file = open("l3.json","w")
    data = json.dumps(l3dict, indent=4)
    file.write(data)
    file.close()