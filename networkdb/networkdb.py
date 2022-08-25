# !/usr/bin/env python3
# v1.0.0

import os, pandas as pd, re
from getpass import getpass, getuser
from acidata import apics, headers, nodes, acidata
from l3data import core, l3data
from l2data import devices, l2data
from dnsdata import recordstoignore, dnsdict, dnsdata

# The purpose of this script is to call all the others and store the data in a Excel file.

try:
    os.chdir(f"/mnt/c/Users/{getuser()}/Documents/networking/networkdb")
except(FileNotFoundError):
    os.chdir(os.getcwd())

user = input("TACACS user: ")
pas = getpass(prompt="TACACS password: ")
dnsuser = input("Infoblox user: ")
dnspas = getpass(prompt="Infoblox password: ")

# The ARP data, MAC and DNS (A records) will be stored in individual dataframes.

l3df = []
l3data(user,pas,core,l3df)
l3df = pd.DataFrame(l3df)
l3df = l3df[l3df["mac"].str.contains("Incomplete")==False]
l3df = l3df[l3df["mac"].str.contains("INCOMPLETE")==False]

l2df =[]
l2data(user,pas,devices,l2df)
l2df = pd.DataFrame(l2df)
l2df["sw"] = l2df["sw"].replace(regex={r"#":""})

dnsdata(dnsuser,dnspas,recordstoignore,dnsdict)
dnsdf = []
for entry in dnsdict.items():
    dnsdf.append({"ip":entry[0],"dns":entry[1]})
dnsdf = pd.DataFrame(dnsdf)

# The ACI data will be stored in its own dataframe, the data coming from ACI will be processed to fit the requeriments needed 
# for the merging of data.

acidf, leafs, dotmacs = [],[],[]
acidata(user,pas,apics,headers,acidf)
acidf = pd.DataFrame(acidf)
acidf[["sw", "interface"]] = acidf["interface"].str.split('/pathep-', 1, expand=True)
acidf["sw"] = acidf["sw"].replace(regex=["topology/pod-\d/","protpaths-","paths-"],value="")
for sw in acidf["sw"]:
    lfs = []
    ids = sw.split("-")
    for id in range(len(ids)):
        leaf = re.sub(ids[id],nodes[ids[id]],ids[id])
        lfs.append(leaf)
    leafs.append(lfs)
acidf["sw"] = leafs

acidf["sw"] = acidf["sw"].replace(regex={r"\[":"",r"\]":"","', '":"/"})
acidf["interface"] = acidf["interface"].replace(regex={r"\[":"",r"\]":"","eth":"Eth"})

acidf["mac"] = acidf["mac"].str.lower()
for mac in acidf["mac"]:
    dotmac = mac.split(":")
    mac = dotmac[0]+dotmac[1]+"."+dotmac[2]+dotmac[3]+"."+dotmac[4]+dotmac[5]
    dotmacs.append(mac)
acidf["mac"] = dotmacs
acidf["vlan"] = acidf["vlan"].replace(regex={r"vlan-":"Vlan"})

acidf_c = acidf.copy()
acidf_c["dns"] = "--"
acidf_c = acidf_c[["ip","mac","vlan","dns","sw","interface"]]

# To make sure that the data will be properly merged new columns will be created based on the MAC and VLAN columns.

acidf["join"] = acidf["mac"]+acidf["vlan"]
l2df["join"] = l2df["mac"]+l2df["vlan"]
l3df["join"] = l3df["mac"]+l3df["vlan"]

# The legacydf stores data about the devices connected in legacy networks (non-ACI),
# since the inner joins will drop data about IPs that don't have a DNS A record a copy of the dataframe is created,
# said copy will have a DNS column with non-relevant data to make sure the concatenation goes well.

legacydf = l3df.merge(l2df,how="inner",on="join")
l3l2df = legacydf.copy()
l3l2df["dns"] = "--"
legacydf = legacydf.merge(dnsdf,how="inner",left_on="ip_x",right_on="ip")
legacydf = legacydf.drop(columns=["ip_x","vlan_x","mac_x","join","ip_y"])
legacydf = legacydf.rename(columns={"mac_y":"mac","vlan_y":"vlan"})
legacydf = legacydf[["ip","mac","vlan","dns","sw","interface"]]
l3l2df = l3l2df.drop(columns=["vlan_x","mac_x","join","ip_y"])
l3l2df = l3l2df.rename(columns={"mac_y":"mac","vlan_y":"vlan","ip_x":"ip"})
l3l2df = l3l2df[["ip","mac","vlan","dns","sw","interface"]]
legacydf = pd.concat([legacydf,l3l2df])
legacydf = legacydf.drop_duplicates(subset=["ip"], keep="first")

# The newdf stores data about the devices connected in ACI networks,
# since the inner joins will drop data about IPs that don't have a DNS A record a copy of the dataframe is created,
# said copy will have a DNS column with non-relevant data to make sure the concatenation goes well.

newdf = acidf.merge(l3df,how="inner",on="join")
newdf_c = newdf.copy()
newdf_c["dns"] = "--"
newdf_c = newdf_c.drop(columns=["vlan_x","mac_x","join","ip_y"])
newdf_c = newdf_c.rename(columns={"mac_y":"mac","vlan_y":"vlan","ip_x":"ip"})
newdf_c = newdf_c[["ip","mac","vlan","dns","sw","interface"]]
newdf = newdf.merge(dnsdf,how="inner",left_on="ip_y",right_on="ip")
newdf = newdf.rename(columns={"mac_y":"mac","vlan_y":"vlan"})
newdf = newdf[["ip","mac","vlan","dns","sw","interface"]]
newdf = pd.concat([newdf,newdf_c])
acidf = acidf.drop(columns=["join"])
acidf = acidf.merge(dnsdf,how="inner",on="ip")
acidf = acidf[["ip","mac","vlan","dns","sw","interface"]]
acidf = pd.concat([acidf,acidf_c])
acidf = acidf.drop_duplicates(subset=["ip"], keep="first")
newdf = pd.concat([acidf,newdf])
newdf = newdf.drop_duplicates(subset=["ip"], keep="first")

# The end result is a Excel file that has the logical location of all endpoints in the DC network.

writer = pd.ExcelWriter("networkdb.xlsx", engine='xlsxwriter')
legacydf.to_excel(writer,sheet_name="Legacy",index=None,header=True,freeze_panes=(1,0))
newdf.to_excel(writer,sheet_name="ACI",index=None,header=True,freeze_panes=(1,0))
writer.save()
print("Done")