#!/usr/bin/env python3
#v1.0.1

import concurrent.futures, re, socket, time
from getpass import getpass
from napalm import get_network_driver
from netmiko.ssh_exception import NetmikoTimeoutException, AuthenticationException
from napalm.base.exceptions import ConnectionException
from tqdm import tqdm

user = input("Username: ")
pas = getpass()
ios,nxos,offline,Ddata = [],[],[],[]

with open("ios.txt","r") as file:
    for ip in file:
        ios.append(ip.strip("\n"))
with open("nxos.txt","r") as file:
    for ip in file:
        nxos.append(ip.strip("\n"))
devices = ios+nxos
offline_file = open("offline.txt","w")
offline_file.close()

def data(conn,sw):
    time.sleep(1.5)
    conn.open()
    devicedata = conn.get_facts()
    hostname,serialNumber,model = devicedata["hostname"],devicedata["serial_number"],devicedata["model"]
    try:
        if sw in ios:
            osdata = re.search(r"(.+)(,)(\s)(Version )(.+)(,)(.+)",devicedata["os_version"])
            osVersion = osdata.group(5)
            if int(osVersion.split(".")[0]) >= 16:
                osFamily = "iosxe"
            else:
                osFamily = "ios"
        elif sw in nxos:
            osVersion = devicedata["os_version"]
            osFamily = "nxos"
        Ddata.append({"Hostname":hostname,"IP":sw,"Model":model,
        "SerialNumber":serialNumber,"OS":osFamily,"Version":osVersion})

    except(AttributeError):
        offline_file = open("offline.txt","a")
        offline_file.write(f"Error:{sw}:AttributeError"+"\n")
        offline_file.close()
    except(ValueError):
        offline_file = open("offline.txt","a")
        offline_file.write(f"Error:{sw}:Couldn't get to enable mode"+"\n")
        offline_file.close()
    conn.close()

def connection(sw,ios,nxos,offline,offline_file):
    try:
        if sw in ios:
            driver = get_network_driver("ios")
        elif sw  in nxos:
            driver = get_network_driver("nxos_ssh")
        conn = driver(hostname= sw,username= user, password= pas, optional_args= {"global_delay_factor": 6})
        data(conn,sw)
    except(ConnectionRefusedError, ConnectionResetError):
        offline.append(sw)
        offline_file = open("offline.txt","a")
        offline_file.write(f"Error:{sw}:ConnectionRefused error"+"\n")
        offline_file.close()
    except(TimeoutError, socket.timeout):
        offline.append(sw)
        offline_file = open("offline.txt","a")
        offline_file.write(f"Error:{sw}:Timeout error"+"\n")
        offline_file.close()
    except(AuthenticationException):
        offline.append(sw)
        offline_file = open("offline.txt","a")
        offline_file.write(f"Error:{sw}:Authentication error"+"\n")
        offline_file.close()
    except(ConnectionException, NetmikoTimeoutException):
        try:
            driver = get_network_driver("ios")
            conn = driver(hostname= sw,username= user, password= pas, optional_args= {"transport": 'telnet', "global_delay_factor": 6})
            conn.open()
            data(conn,sw)
        except(ConnectionRefusedError, ConnectionResetError):
            offline.append(sw)
            offline_file = open("offline.txt","a")
            offline_file.write(f"Error:{sw}:ConnectionRefused error"+"\n")
            offline_file.close()
        except(TimeoutError, socket.timeout):
            offline.append(sw)
            print(f"Error:{sw}:Timeout error")
            offline_file.write(f"Error:{sw}:Timeout error"+"\n")
            offline_file.close()
        except(AuthenticationException):
            offline.append(sw)
            offline_file = open("offline.txt","a")
            offline_file.write(f"Error:{sw}:Authentication error"+"\n")
            offline_file.close()
    except(EOFError):
        offline.append(sw)
        print(f"Error:{sw}:EOF error")
        offline_file = open("offline.txt","a")
        offline_file.write(f"Error:{sw}:EOF error"+"\n")
        offline_file.close()


def device_data(devices,ios,nxos,offline,offline_file):

    with tqdm(total=len(devices), desc="Extracting device data") as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
            ejecucion = {executor.submit(connection,sw,ios,nxos,offline,offline_file): sw for sw in devices}
        for output_ios in concurrent.futures.as_completed(ejecucion):
            output_ios.result()
            pbar.update(1)