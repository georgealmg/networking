#!/usr/bin/env python3
#v1.0.1

import json, re, socket, time
from getpass import getpass
from napalm import get_network_driver
from netmiko.ssh_exception import NetmikoTimeoutException, AuthenticationException
from napalm.base.exceptions import ConnectionException
        
user = input("Username: ")
pas = getpass()
sw_list = {}
ios = []
nxos = []

with open("ios.txt","r") as file1:
    for ip in file1:
        ios.append(ip.strip("\n"))
        sw_list[ip.strip("\n")] = {}

with open("nexus.txt","r") as file2:
    for ip in file2:
        nxos.append(ip.strip("\n"))
        sw_list[ip.strip("\n")] = {}

with open("modeldata.json","r") as file3:
    modeldata = json.loads(file3.read())

sw_out = []
swout_file = open("sw_out.txt","w")
swout_file.close()

def data(conn,sw):
    time.sleep(1.5)
    conn.open()
    devicedata = conn.get_facts()
    try:
        sw_list[sw]["hostname"],sw_list[sw]["serial"] = devicedata["hostname"],devicedata["serial_number"]
        if devicedata["model"] in modeldata.keys():
            model = devicedata["model"]
            sw_list[sw]["model"] = modeldata[model]
        elif devicedata["model"] not in modeldata.keys():
            sw_list[sw]["model"] = devicedata["model"]

        if sw in ios:
            osdata = re.search(r"(.+)(,)(\s)(Version )(.+)(,)(.+)",devicedata["os_version"])
            version = osdata.group(5)
            sw_list[sw]["version"] = version
            if version.split(".")[0] == "17" or version.split(".")[0] == "16":
                sw_list[sw]["os"] = "iosxe"
            else:
                sw_list[sw]["os"] = "ios"
        elif sw in nxos:
            sw_list[sw]["version"] = devicedata["os_version"]
            sw_list[sw]["os"] = "nxos"
        print("Data extracted --> "+sw_list[sw]["hostname"])

    except(AttributeError):
        swout_file = open("sw_out.txt","a")
        swout_file.write(f"Error:{sw}:AttributeError"+"\n")
        swout_file.close()
    except(ValueError):
        swout_file = open("sw_out.txt","a")
        swout_file.write(f"Error:{sw}:Couldn't get to enable mode"+"\n")
        swout_file.close()
    conn.close()


def device_data(sw,sw_out,ios,nxos):
    try:
        if sw in ios:
            driver = get_network_driver("ios")
        elif sw  in nxos:
            driver = get_network_driver("nxos_ssh")
        conn = driver(hostname= sw,username= user, password= pas, optional_args= {"global_delay_factor": 6})
        data(conn,sw)
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
    except(ConnectionException, NetmikoTimeoutException):
        try:
            driver = get_network_driver("ios")
            conn = driver(hostname= sw,username= user, password= pas, optional_args= {"transport": 'telnet', "global_delay_factor": 6})
            conn.open()
            data(conn,sw)
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