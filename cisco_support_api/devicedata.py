#!/usr/bin/env python3
#v1.0.1

import re, socket, time
from getpass import getpass
from napalm import get_network_driver
from netmiko.ssh_exception import NetmikoTimeoutException, AuthenticationException
from napalm.base.exceptions import ConnectionException
        
user = input("Username: ")
pas = getpass()
ios,nxos,offline,Ddata = [],[],[],[],[]

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
    hostname,serial_number,model = devicedata["hostname"],devicedata["serial_number"],devicedata["model"]
    try:
        if sw in ios:
            osdata = re.search(r"(.+)(,)(\s)(Version )(.+)(,)(.+)",devicedata["os_version"])
            version = osdata.group(5)
            if int(version.split(".")[0]) >= 16:
                os = "iosxe"
            else:
                os = "ios"
        elif sw in nxos:
            version = devicedata["os_version"]
            os = "nxos"
        Ddata.append({"Hostname":hostname,"IP":sw,"Model":model,
        "SerialNumber":serial_number,"OS":os,"Version":version})

    except(AttributeError):
        swout_file = open("offline.txt","a")
        swout_file.write(f"Error:{sw}:AttributeError"+"\n")
        swout_file.close()
    except(ValueError):
        swout_file = open("offline.txt","a")
        swout_file.write(f"Error:{sw}:Couldn't get to enable mode"+"\n")
        swout_file.close()
    conn.close()


def device_data(sw,offline_file,ios,nxos):
    try:
        if sw in ios:
            driver = get_network_driver("ios")
        elif sw  in nxos:
            driver = get_network_driver("nxos_ssh")
        conn = driver(hostname= sw,username= user, password= pas, optional_args= {"global_delay_factor": 6})
        data(conn,sw)
    except(ConnectionRefusedError, ConnectionResetError):
        offline_file.ppend(sw)
        swout_file = open("offline.txt","a")
        swout_file.write(f"Error:{sw}:ConnectionRefused error"+"\n")
        swout_file.close()
    except(TimeoutError, socket.timeout):
        offline_file.ppend(sw)
        swout_file = open("offline.txt","a")
        swout_file.write(f"Error:{sw}:Timeout error"+"\n")
        swout_file.close()
    except(AuthenticationException):
        offline_file.ppend(sw)
        print(f"Error:{sw}:Authentication error")
        swout_file = open("offline.txt","a")
        swout_file.write(f"Error:{sw}:Authentication error"+"\n")
        swout_file.close()
    except(ConnectionException, NetmikoTimeoutException):
        try:
            driver = get_network_driver("ios")
            conn = driver(hostname= sw,username= user, password= pas, optional_args= {"transport": 'telnet', "global_delay_factor": 6})
            conn.open()
            data(conn,sw)
        except(ConnectionRefusedError, ConnectionResetError):
            offline_file.ppend(sw)
            print(f"Error:{sw}:ConnectionRefused error")
            swout_file = open("offline.txt","a")
            swout_file.write(f"Error:{sw}:ConnectionRefused error"+"\n")
            swout_file.close()
        except(TimeoutError, socket.timeout):
            offline_file.ppend(sw)
            print(f"Error:{sw}:Timeout error")
            swout_file = open("offline.txt","a")
            swout_file.write(f"Error:{sw}:Timeout error"+"\n")
            swout_file.close()
        except(AuthenticationException):
            offline_file.ppend(sw)
            print(f"Error:{sw}:Authentication error")
            swout_file = open("offline.txt","a")
            swout_file.write(f"Error:{sw}:Authentication error"+"\n")
            swout_file.close()
    except(EOFError):
        offline_file.ppend(sw)
        print(f"Error:{sw}:EOF error")
        swout_file = open("offline.txt","a")
        swout_file.write(f"Error:{sw}:EOF error"+"\n")
        swout_file.close()