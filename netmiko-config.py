from netmiko import ConnectHandler
from netmiko.ssh_exception import SSHException, AuthenticationException, NetmikoTimeoutException
from datetime import datetime
import getpass, os, sys, concurrent.futures

#Funcion que configuraran/validaran las rutas.
def NXOS(sw_n,user,pas,fp,fp1,fp2,comandos_nx,segmentos):
    def rutas(net_connect):
        hostname = net_connect.find_prompt()
        print(f"Ejecutando en {hostname} : {sw_n}")
        output = net_connect.send_config_set(comandos_nx)
        fp.write(hostname+" "+sw_n+"\n"+output+"\n")
        for seg in segmentos:
            validacion = net_connect.send_command("show ip route %s" % seg) 
            if "1.1.1.1" not in validacion:
                fp1.write(hostname+" "+sw_n+"\n"+validacion+"\n")
        clock = net_connect.send_command("show clock")
        run = net_connect.send_command("show running-config")
        start = net_connect.send_command("show startup-config")
        fp2.write(hostname+" "+sw_n+"\n"+clock+"\n"+net_connect.save_config()+"\n"+run+"\n"+start)
        print(f"Ejecucion finalizada en {hostname} : {sw_n}")
        net_connect.disconnect()
    try:
        net_connect = ConnectHandler(device_type= "cisco_nxos_ssh",host= sw_n,username= user,password= pas, fast_cli=False)
        rutas(net_connect)
    except(AuthenticationException):
        sys.exit("Por favor ejecute nuevamente el programa ya que introdujo una contraseña erronea.")
    except(SSHException, NetmikoTimeoutException):
        try:
            net_connect = ConnectHandler(device_type="cisco_nxos_telnet", host= sw_n, username= user, password= pas, fast_cli=False)
            rutas(net_connect)
        except:
            print(f"Switch con IP: {sw_n} esta fuera de linea")
            fp1.write(sw_n+"\n")

def main():

    windowsuser = os.getlogin()
    os.chdir("C:/Users/"+windowsuser+"/Documents")
    user = input("Username: ")
    pas = getpass.getpass()

    #Lista de SW a intervenir.
    sw_nx = []
    comandos_nx = []
    segmentos =[]
    
    #TXT donde se aloja evidencias de lo ejecutado.
    fp = open("config.txt","w+")
    fp1 = open("validacion_rutas.txt","w+")
    fp2 = open("Evidencia_de_respaldos.txt","w+")
    total_sw = len(sw_nx)
    tiempo1 = datetime.now()
    tiempo_inicial = tiempo1.strftime("%H:%M:%S")
    print(f"La ejecucion de este programa inicio a las {tiempo_inicial}, se validara un total de {str(total_sw)} switch.")
    
    #Funcion que permit ipen la ejecucion de las configuraciones por medio de 4 procesos asincronos.
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor_nx:
        ejecucion_nx = {executor_nx.submit(NXOS,sw_n,user,pas,fp,fp1,fp2,comandos_nx,segmentos): sw_n for sw_n in sw_nx}
    for output_nx in concurrent.futures.as_completed(ejecucion_nx):
        output_nx.result()

    fp.close()
    fp1.close()
    fp2.close()
    tiempo2 = datetime.now()
    tiempo_final = tiempo2.strftime("%H:%M:%S")
    print(f"La ejecucion de este programa finalizo a las {tiempo_final}, se validaron un total de {str(total_sw)}")
    tiempo_ejecucion = tiempo2 - tiempo1
    print(f"El tiempo de ejecucion del programa fue de: {tiempo_ejecucion}")

if __name__ == "__main__":
    main()
