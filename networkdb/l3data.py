#!/usr/bin/env python3
#v1.0.2

from netmiko import ConnectHandler
from netmiko.ssh_exception import SSHException, AuthenticationException
from ntc_templates.parse import parse_output
from tqdm import tqdm

core = {"nxos":[], "ios":[]}

# This script will retrieve the arp tables.
def l3data_nxos(user,pas,core,l3df):

    with tqdm(total=len(core["nxos"]),desc="L3data nxos") as pbar:
        for device in core["nxos"]:
            conn = ConnectHandler(device_type="cisco_nxos_ssh" ,host=device ,username=user ,password=pas,fast_cli=False)
            arp = parse_output(platform="cisco_nxos",command="show ip arp",data=conn.send_command(f"show ip arp"))
            for entry in arp:
                inter = entry["interface"]
                ip = entry["address"]
                mac = entry["mac"]
                l3df.append({"ip":ip,"vlan":inter,"mac":mac})
            conn.disconnect()
            pbar.update(1)

def l3data_ios(user,pas,core,l3df):

    with tqdm(total=len(core["ios"]),desc="L3data ios") as pbar:
        for device in core["ios"]:
            conn = ConnectHandler(device_type="cisco_ios_ssh" ,host=device ,username=user ,password=pas)
            arp = parse_output(platform="cisco_ios",command="show ip arp",data=conn.send_command(f"show ip arp"))
            for entry in arp:
                inter = entry["interface"]
                ip = entry["address"]
                mac = entry["mac"]
                l3df.append({"ip":ip,"vlan":inter,"mac":mac})
            conn.disconnect()
            pbar.update(1)

def l3data(user,pas,core,l3df):
    try:
        l3data_nxos(user,pas,core,l3df)
        l3data_ios(user,pas,core,l3df)
    except(ConnectionRefusedError):
        pass
    except(AuthenticationException):
            pass
    except(SSHException):
        pass
    except(EOFError):
        pass