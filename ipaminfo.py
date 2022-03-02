#!/usr/bin/env python3
#v1.0.0

import concurrent.futures, csv, requests
from getpass import getpass
from netmiko import ConnectHandler
from netmiko.ssh_exception import SSHException, AuthenticationException
from ntc_templates.parse import parse_output
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


core = {"nxos":{},"ios":{}}
l3arp, ipam = {}, {}
l3route, route_notin_infoblox = [], []

user = input("TACACS user: ")
pas = getpass(prompt="TACACS password: ")
dnsuser = input("Infoblox user: ")
dnspas = getpass(prompt="Infoblox password: ")

def l3data_nxos(user,pas,core,l3arp,l3route):
    for device in core["nxos"]:
        conn = ConnectHandler(device_type="cisco_nxos_ssh" ,host=device ,username=user ,password=pas)
        arp = parse_output(platform="cisco_nxos",command="show ip arp",data=conn.send_command(f"show ip arp"))
        for entry in arp:
            if entry["interface"] not in l3arp["nxos"].keys():
                l3arp["nxos"][entry["address"]] = {}
                l3arp["nxos"][entry["address"]]["mac"] = entry["mac"]
            elif entry["interface"] in l3arp["nxos"].keys():
                pass
        route = parse_output(platform="cisco_nxos",command="show ip route",data=conn.send_command(f"show ip route direct"))
        for entry in route:
            if entry["protocol"] == "direct":
                connected_route = entry["network"] +"/"+ entry["mask"]
                if connected_route not in l3route["nxos"]:
                    l3route["nxos"].append(connected_route)
                elif connected_route in l3route["nxos"]:
                    pass
            elif entry["protocol"] != "direct":
                pass
        print(f"Data l3 extraida --> {conn.find_prompt()}")
        conn.disconnect()

def l3data_ios(user,pas,core,l3arp,l3route):
    for device in core["ios"]:
        conn = ConnectHandler(device_type="cisco_ios_ssh" ,host=device ,username=user ,password=pas)
        arp = parse_output(platform="cisco_ios",command="show ip arp",data=conn.send_command(f"show ip arp"))
        for entry in arp:
            if entry["interface"] not in l3arp["ios"].keys():
                l3arp["ios"][entry["address"]] = {}
                l3arp["ios"][entry["address"]]["mac"] = entry["mac"]
            elif entry["interface"] in l3arp["ios"].keys():
                pass
        route = parse_output(platform="cisco_ios",command="show ip route",data=conn.send_command(f"show ip route"))
        for entry in route:
            if entry["protocol"] == "C":
                connected_route = entry["network"] +"/"+ entry["mask"]
                if connected_route not in l3route["ios"]:
                    l3route["ios"].append(connected_route)
                elif connected_route in l3route["ios"]:
                    pass
            elif entry["protocol"] != "C":
                pass
        print(f"Data l3 extraida --> {conn.find_prompt()}")
        conn.disconnect()

def l3data(user,pas,core,l3arp,l3route):
    try:
        l3data_nxos(user,pas,core,l3arp,l3route)
        l3data_ios(user,pas,core,l3arp,l3route)
    except(ConnectionRefusedError):
        print(f"Error --> ConnectionRefused error")
    except(AuthenticationException):
        print(f"Error --> Authenticacion error")
    except(SSHException):
        print(f"Error --> ConnectionRefused error")
    except(EOFError):
        print(f"Error --> EOF error")

l3data(user,pas,core,l3arp,l3route)

def ipamdata(route,dnsuser,dnspas,ipam,route_notin_infoblox):

    ipam[route] = {}
    url = f"https://10.40.16.107/wapi/v2.11/ipv4address?network={route}/23&_return_as_object=1"
    response = requests.request("GET", url, auth=(dnsuser, dnspas), verify=False)
    try:
        for entry in response.json()["result"]:
            if "NETWORK" not in entry["types"] or "BROADCAST" not in entry["types"]:
                ipam[route][entry["ip_address"]] = {}
                ipam[route][entry["ip_address"]]["status"] = entry["status"]
                if "FA" in entry["types"]:
                    ipam[route][entry["ip_address"]]["type"] = "Fixed address"
                elif "RESERVATION" in entry["types"]:
                    ipam[route][entry["ip_address"]]["type"] = "Reservation"
                elif "A" == entry["types"]:
                    ipam[route][entry["ip_address"]]["type"] = "A record"
                elif "PTR" == entry["types"]:
                    ipam[route][entry["ip_address"]]["type"] = "PTR record"
                elif "UNMANAGED" in entry["types"]:
                    ipam[route][entry["ip_address"]]["type"] = "Unmanaged"
                elif entry["types"] == []:
                    ipam[route][entry["ip_address"]]["type"] = "--"
            elif "NETWORK" in entry["types"] or "BROADCAST" in entry["types"]:
                pass
        print(f"Data extraida --> {route}")
    except(KeyError):
        route_notin_infoblox.append(route)

def main():
    
    print("IPAM DATA", f"Cantidad de segmentos: {str(len(l3route))}",sep="\n")

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        ejecucion = {executor.submit(ipamdata,route,dnsuser,dnspas,ipam,route_notin_infoblox): route for route in l3route}
    for output in concurrent.futures.as_completed(ejecucion):
            output.result()

    print("IPAM DATA", f"Cantidad de data extraida: {str(len(l3route)-len(route_notin_infoblox))}",sep="\n")

if __name__ == "__main__":
    main()

data_file = open("ipaminfo.csv","w", newline='',encoding="utf-8")
first_row = ["segment","ip","status","mac","type","names"]
writer = csv.DictWriter(data_file, fieldnames=first_row, restval="Error")
writer.writeheader()

for route in l3route:
    for route2 in ipam.keys():
        if route == route2:
            for ip in ipam[route].keys():
                try:
                    status = ipam[route][ip]["status"]
                except(KeyError):
                    status = "--"
                try:
                    types = ipam[route][ip]["type"]
                except(KeyError):
                     types = "--"
                if ipam[route][ip]["names"] == []:
                    names = ipam[route][ip]["names"]
                if ipam[route][ip]["names"] == []:
                    names = ipam[route][ip]["names"]
                try:
                    mac = l3arp[ip]["mac"]
                except(KeyError):
                    mac = "--"
                writer.writerow({"segment":route,"ip":ip,"status":status,
                "mac":mac,"type":types,"names":names})

data_file.close()