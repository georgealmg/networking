#!/usr/bin/env python3

import concurrent.futures, socket
from tqdm import tqdm
from unicon.core.errors import ConnectionError, TimeoutError

offline,Ddata = [],[]
offline_file = open("offline.txt","w")
offline_file.close()
models_replace = ["C3560","C3750"]

def data(conn):
    output = conn.parse('show version')
    try:
        if "version" in output.keys():
            hostname = output["version"]["hostname"]
            model = output["version"]["chassis"]
            for m in models_replace:
                if m in model:
                    for key in output["version"]["switch_num"].keys():
                        if m in output["version"]["switch_num"][key]["model_num"]:
                            model = output["version"]["switch_num"][key]["model_num"]
                            break
            serial = output["version"]["chassis_sn"]
            os = output["version"]["os"]
            version = output["version"]["version"]
        elif "platform" in output.keys():
            hostname = output["platform"]["hardware"]["device_name"]
            model = output["platform"]["hardware"]["chassis"]
            serial = output["platform"]["hardware"]["processor_board_id"]
            os = output["platform"]["os"]
            version = output["platform"]["software"]["system_version"]
        Ddata.append({"Hostname":hostname,"ProductID":model,"SerialNumber":serial,"OS":os,"OSVersion":version})
    except(KeyError):
        pass
    conn.disconnect()

def connection(device,offline,offline_file,tb):
    try:
        conn = tb.devices[device]
        conn.connect(log_stdout=False)
        data(conn)
    except(ConnectionError):
        offline.append(device)
        offline_file = open("offline.txt","a")
        offline_file.write(f"{device},ConnectionRefused error"+"\n")
        offline_file.close()
    except(TimeoutError, socket.timeout):
        offline.append(device)
        offline_file = open("offline.txt","a")
        offline_file.write(f"{device},Timeout error"+"\n")
        offline_file.close()

def device_data(devices,offline,offline_file,tb):

    with tqdm(total=len(devices), desc="Extracting device data") as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
            ejecucion = {executor.submit(connection,device,offline,offline_file,tb): device for device in devices}
        for output in concurrent.futures.as_completed(ejecucion):
            output.result()
            pbar.update(1)