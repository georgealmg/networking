#!/usr/bin/env python3
#v1.0.1

from netmiko import ConnectHandler
from netmiko.exceptions import SSHException, AuthenticationException
from ntc_templates.parse import parse_output
from socket import timeout
from tqdm import tqdm

core = {"nxos":[], "ios":[]}

# This script will retrieve the arp tables.
def l3data(user,pas,core,l3df,out):

    with tqdm(total=len(core["nxos"]+len(["ios"])),desc="L3data") as pbar:
        try:
            for device in core["nxos"]:
                conn = ConnectHandler(device_type="cisco_nxos_ssh", host=device, username=user, password=pas, fast_cli=False)
                arp = parse_output(platform="cisco_nxos",command="show ip arp",data=conn.send_command(f"show ip arp"))
                for entry in arp:
                    inter = entry["interface"]
                    ip = entry["address"]
                    mac = entry["mac"]
                    l3df.append({"ip":ip,"vlan":inter,"mac":mac})
                conn.disconnect()
                pbar.update(1)
        
            for device in core["ios"]:
                conn = ConnectHandler(device_type="cisco_ios_ssh", host=device, username=user, password=pas, fast_cli=False)
                arp = parse_output(platform="cisco_ios",command="show ip arp",data=conn.send_command(f"show ip arp"))
                for entry in arp:
                    inter = entry["interface"]
                    ip = entry["address"]
                    mac = entry["mac"]
                    l3df.append({"ip":ip,"vlan":inter,"mac":mac})
                conn.disconnect()
                pbar.update(1)

        except(AuthenticationException):
            out.append({"device":device,"error":"Authentication error"})
            pbar.update(1)
        except(TimeoutError, timeout):
            out.append({"device":device,"error":"Timeout error"})
            pbar.update(1)
        except(ConnectionRefusedError, SSHException):
            out.append({"device":device,"error":"ConnectionRefused error"})
            pbar.update(1)
        except(EOFError):
            out.append({"device":device,"error":"EOF error"})
            pbar.update(1)
        except(OSError):
            out.append({"device":device,"error":"OS error"})
            pbar.update(1)