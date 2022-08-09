#!/usr/bin/ python3
#v1.0.9

import concurrent.futures, os, socket
from getpass import getuser
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetmikoTimeoutException, SSHException, AuthenticationException
from ntc_templates.parse import parse_output
from tqdm import tqdm

try:
    os.chdir("C:/Python")
except(FileNotFoundError):
    try:
        os.chdir(f"/mnt/c/Users/{getuser()}/Documents/Python")
    except(FileNotFoundError):
        os.chdir(os.getcwd())

ios,nxos = [],[]
l2df = []
devices = ios+nxos

def data(conn,device,l2df,pbar):

    hostname = conn.find_prompt()
    if device in ios:
        channels = parse_output(platform="cisco_ios",command="show etherchannel summary",data=conn.send_command("show etherchannel summary"))
        cdp = parse_output(platform="cisco_ios",command="show cdp neighbors",data=conn.send_command("show cdp neighbors"))
    elif device in nxos:
        channels = parse_output(platform="cisco_nxos",command="show port-channel summary",data=conn.send_command("show port-channel summary"))
        cdp = parse_output(platform="cisco_nxos",command="show cdp neighbors",data=conn.send_command("show cdp neighbors"))
    
    uplinks = []
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

    if device in ios:
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
                l2df.append({"sw":hostname,"ip":device,"interface":dstport,"mac":macentry["destination_address"],
                "vlan":"Vlan"+macentry["vlan"]})
    elif device in nxos:
        for channelsentry in channels:
            for physinter in channelsentry["phys_iface"]:
                if physinter in uplinks:
                    uplinks.append(channelsentry["bundle_iface"])
        vlanmac = parse_output(platform="cisco_nxos",command="show mac address-table",data=conn.send_command("show mac address-table"))
        for macentry in vlanmac:
            if "vPC" not in macentry["ports"] or "sup-eth" not in macentry["ports"]:
                if macentry["ports"] not in uplinks:
                    l2df.append({"sw":hostname,"ip":device,"interface":macentry["ports"],"mac":macentry["mac"],
                    "vlan":"Vlan"+macentry["vlan"]})
    
    conn.disconnect()
    pbar.update(1)

def connection(user,pas,device,l2df,pbar):
    try:
        if device in ios:
            conn = ConnectHandler(device_type="cisco_ios_ssh" ,host=device ,username=user ,password=pas , fast_cli= False)
            data(conn,device,l2df,pbar)
        elif device in nxos:
            conn = ConnectHandler(device_type="cisco_nxos_ssh" ,host=device ,username=user ,password=pas , fast_cli= False)
            data(conn,device,l2df,pbar)
    except(ConnectionRefusedError, ConnectionResetError):
        swout_file = open("sw_out.txt","a")
        swout_file.write(f"Error:{device}:ConnectionRefused error"+"\n")
        swout_file.close()
        pbar.update(1)
    except(TimeoutError, socket.timeout):
        swout_file = open("sw_out.txt","a")
        swout_file.write(f"Error:{device}:Timeout error"+"\n")
        swout_file.close()
        pbar.update(1)
    except(AuthenticationException):
        swout_file = open("sw_out.txt","a")
        swout_file.write(f"Error:{device}:Authenticacion error"+"\n")
        swout_file.close()
        pbar.update(1)
    except(SSHException, NetmikoTimeoutException):
        try:
            conn = ConnectHandler(device_type="cisco_ios_telnet" ,host=device ,username=user ,password=pas , fast_cli= False)
            data(conn,device)
        except(ConnectionRefusedError, ConnectionResetError):
            swout_file = open("sw_out.txt","a")
            swout_file.write(f"Error:{device}:ConnectionRefused error"+"\n")
            swout_file.close()
            pbar.update(1)
        except(TimeoutError, socket.timeout):
            swout_file = open("sw_out.txt","a")
            swout_file.write(f"Error:{device}:Timeout error"+"\n")
            swout_file.close()
            pbar.update(1)
        except(AuthenticationException):
            swout_file = open("sw_out.txt","a")
            swout_file.write(f"Error:{device}:Authenticacion error"+"\n")
            swout_file.close()
            pbar.update(1)
        except(OSError):
            swout_file = open("sw_out.txt","a")
            swout_file.write(f"Error:{device}:OS error"+"\n")
            swout_file.close()
            pbar.update(1)
    except(EOFError):
        swout_file = open("sw_out.txt","a")
        swout_file.write(f"Error:{device}:EOF error"+"\n")
        swout_file.close()
        pbar.update(1)
    except(OSError):
        swout_file = open("sw_out.txt","a")
        swout_file.write(f"Error:{device}:OS error"+"\n")
        swout_file.close()
        pbar.update(1)

def l2data(user,pas,devices,l2df):

    with tqdm(total=len(devices),desc="L2data") as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            ejecucion = {executor.submit(connection,user,pas,device,l2df,pbar): device for device in devices}
        for output in concurrent.futures.as_completed(ejecucion):
            output.result()