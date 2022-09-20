# !/usr/bin/env python3
# v1.0.1

import os, pandas as pd, sqlalchemy as db, re
from dotenv import load_dotenv
from getpass import getuser
from netifaces import gateways
from acidata import apics, headers, nodes, acidata
from l3data import core, l3data
from l2data import devices, l2data
from dnsdata import recordstoignore, dnsdict, dnsdata

# The purpose of this script is to call all the others and store the data in a Excel file.

try:
    os.chdir(f"/mnt/c/Users/{getuser()}/Documents/networking/networkdb")
except(FileNotFoundError):
    os.chdir(os.getcwd())

load_dotenv("networkdb.env")
user = os.environ["user"]
pas = os.environ["netpass"]
dnsuser = os.environ["dnsuser"]
dnspas = os.environ["dnspass"]
gateway = gateways()["default"][2][0]
engine = db.create_engine(f"mysql+pymysql://root:pr0gr4m@{gateway}/networkdb")
conn = engine.connect()
out = []

# The ARP data, MAC and DNS (A records) will be stored in individual dataframes.
# To make sure that the data will be properly merged new columns (joinkey) will be created based on the MAC and VLAN columns.

l3df = []
l3data(user,pas,core,l3df,out)
l3df = pd.DataFrame(l3df)
l3df = l3df[l3df["mac"].str.contains("Incomplete")==False]
l3df = l3df[l3df["mac"].str.contains("INCOMPLETE")==False]
l3df["joinkey"] = l3df["mac"]+l3df["vlan"]
l3df.to_sql("l3",conn,"networkdb",if_exists="append",index=False)

l2df =[]
l2data(user,pas,devices,l2df,out)
l2df = pd.DataFrame(l2df)
l2df["sw"] = l2df["sw"].replace(regex={r"#":""})
l2df["joinkey"] = l2df["mac"]+l2df["vlan"]
l2df.to_sql("l2",conn,"networkdb",if_exists="append",index=False)

# This csv will store data about the failed connection attempts.
outdf = pd.DataFrame(out)
outdf.to_csv("offline.csv",sep=",",index=False)

dnsdata(dnsuser,dnspas,recordstoignore,dnsdict)
dnsdf = []
for entry in dnsdict.items():
    dnsdf.append({"ip":entry[0],"dns":str(entry[1])})
dnsdf = pd.DataFrame(dnsdf)
dnsdf.to_sql("dns",conn,"networkdb",if_exists="append",index=False)

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
    leafs.append(str(lfs))
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
acidf["joinkey"] = acidf["mac"]+acidf["vlan"]
acidf.to_sql("aci",conn,"networkdb",if_exists="append",index=False)