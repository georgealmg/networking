#!/usr/bin/ python3
#v1.0.0

import concurrent.futures, json, socket
from datetime import datetime
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetmikoTimeoutException, SSHException, AuthenticationException
from ntc_templates.parse import parse_output

acc = {"nxos":[],"ios":[]}
l2dict = {"nxos":{},"ios":{}}

def data(conn,device):

    if device in acc["nxos"]:
        env = "nxos"
    elif device in acc["ios"]:
        env = "ios"
    
    uplinks = []
    if device in acc["ios"]:
        channels = parse_output(platform="cisco_ios",command="show etherchannel summary",data=conn.send_command("show etherchannel summary"))
        cdp = parse_output(platform="cisco_ios",command="show cdp neighbors",data=conn.send_command("show cdp neighbors"))
    elif device in acc["nxos"]:
        channels = parse_output(platform="cisco_nxos",command="show port-channel summary",data=conn.send_command("show port-channel summary"))
        cdp = parse_output(platform="cisco_nxos",command="show cdp neighbors",data=conn.send_command("show cdp neighbors"))
    hostname = conn.find_prompt()
    print(f"Extrayendo data l2 --> {hostname}")
    l2dict[env][hostname] = {}
    l2dict[env][hostname]["interfaces"] = {}
    l2dict[env][hostname]["swip"] = device

    for cdpinter in cdp:
        if "H" not in cdpinter["capability"]:
            if "Fas" in cdpinter["local_interface"]:
                uplink = cdpinter["local_interface"].replace("Fas ","Fa")
            elif "Gig" in cdpinter["local_interface"]:
                uplink = cdpinter["local_interface"].replace("Gig ","Gi")
            elif "Ten" in cdpinter["local_interface"]:
                uplink = cdpinter["local_interface"].replace("Ten ","Te")
            elif "Eth" in cdpinter["local_interface"]:
                uplink = cdpinter["local_interface"].replace("Eth ","Eth")
            else:
                pass
            try:
                uplinks.append(uplink)
            except(UnboundLocalError,NameError):
                pass
        elif "H" in cdpinter["capability"]:
            pass

    if device in acc["ios"]:
        for channelsentry in channels:
            for physinter in channelsentry["interfaces"]:
                if physinter in uplinks:
                    uplinks.append(channelsentry["po_name"])
        vlanmac = parse_output(platform="cisco_ios",command="show mac address-table",data=conn.send_command("show mac address-table"))
        for macentry in vlanmac:
            dstport = macentry["destination_port"][0]
            if "Port-channel" in dstport:
                dstport = macentry["destination_port"][0].replace("Port-channel","Po")
            elif "FastEthernet" in dstport:
                dstport = macentry["destination_port"][0].replace("FastEthernet","Fa")
            elif "GigabitEthernet" in dstport:
                dstport = macentry["destination_port"][0].replace("GigabitEthernet","Gi")
            if dstport not in uplinks and ("CPU" not in dstport and "Switch" not in dstport):
                if dstport not in l2dict[env][hostname]["interfaces"]: 
                    l2dict[env][hostname]["interfaces"][dstport] = {}
                    l2dict[env][hostname]["interfaces"][dstport][macentry["destination_address"]] = "Vlan" + macentry["vlan"]
                elif dstport in l2dict[env][hostname]["interfaces"]: 
                    l2dict[env][hostname]["interfaces"][dstport][macentry["destination_address"]] = "Vlan" + macentry["vlan"]
    elif device in acc["nxos"]:
        for channelsentry in channels:
            for physinter in channelsentry["phys_iface"]:
                if physinter in uplinks:
                    uplinks.append(channelsentry["bundle_iface"])
        vlanmac = parse_output(platform="cisco_nxos",command="show mac address-table",data=conn.send_command("show mac address-table"))
        for macentry in vlanmac:
            if "vPC" in macentry["ports"] or "sup-eth" in macentry["ports"]:
                pass
            elif "vPC" not in macentry["ports"] or "sup-eth" not in macentry["ports"]:
                if macentry["ports"] not in uplinks:
                    if macentry["ports"] not in l2dict[env][hostname]["interfaces"]:
                        l2dict[env][hostname]["interfaces"][macentry["ports"]] = {}
                        l2dict[env][hostname]["interfaces"][macentry["ports"]][macentry["mac"]] = "Vlan" + macentry["vlan"]
                    elif macentry["ports"] in l2dict[env][hostname]["interfaces"]:
                        l2dict[env][hostname]["interfaces"][macentry["ports"]][macentry["mac"]] = "Vlan" + macentry["vlan"]
    
    conn.disconnect()

def l2data(device,sw_out,user,pas):
    try:
        if device in acc["ios"]:
            conn = ConnectHandler(device_type="cisco_ios_ssh" ,host=device ,username=user ,password=pas)
            data(conn,device)
        elif device in acc["nxos"]:
            conn = ConnectHandler(device_type="cisco_nxos_ssh" ,host=device ,username=user ,password=pas)
            data(conn,device)
    except(ConnectionRefusedError, ConnectionResetError):
        sw_out.append(device)
        print(f"Error:{device}:ConnectionRefused error")
        swout_file = open("sw_result.txt","a")
        swout_file.write(f"Error:{device}:ConnectionRefused error"+"\n")
        swout_file.close()
    except(TimeoutError, socket.timeout):
        sw_out.append(device)
        print(f"Error:{device}:Timeout error")
        swout_file = open("sw_result.txt","a")
        swout_file.write(f"Error:{device}:Timeout error"+"\n")
        swout_file.close()
    except(AuthenticationException):
        sw_out.append(device)
        print(f"Error:{device}:Authenticacion error")
        swout_file = open("sw_result.txt","a")
        swout_file.write(f"Error:{device}:Authenticacion error"+"\n")
        swout_file.close()
    except(SSHException, NetmikoTimeoutException):
        try:
            conn = ConnectHandler(device_type="cisco_ios_telnet" ,host=device ,username=user ,password=pas)
            data(conn,device)
        except(ConnectionRefusedError, ConnectionResetError):
            sw_out.append(device)
            print(f"Error:{device}:ConnectionRefused error")
            swout_file = open("sw_result.txt","a")
            swout_file.write(f"Error:{device}:ConnectionRefused error"+"\n")
            swout_file.close()
        except(TimeoutError, socket.timeout):
            sw_out.append(device)
            print(f"Error:{device}:Timeout error")
            swout_file = open("sw_result.txt","a")
            swout_file.write(f"Error:{device}:Timeout error"+"\n")
            swout_file.close()
        except(AuthenticationException):
            sw_out.append(device)
            print(f"Error:{device}:Authenticacion error")
            swout_file = open("sw_result.txt","a")
            swout_file.write(f"Error:{device}:Authenticacion error"+"\n")
            swout_file.close()
    except(EOFError):
        sw_out.append(device)
        print(f"Error:{device}:EOF error")
        swout_file = open("sw_result.txt","a")
        swout_file.write(f"Error:{device}:EOF error"+"\n")
        swout_file.close()