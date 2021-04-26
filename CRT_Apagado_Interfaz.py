crt.Screen.Synchronous = True
interfaz = []
user = crt.Dialog.Prompt("Enter user for SSH: ")
passwd = crt.Dialog.Prompt("Enter password: ")
SSH = []
Telnet = []

def inter(interfaz):
    crt.Dialog.MessageBox("Por favor modifique el txt "+sw+" para que solo contenga las interfaces a intervenir")
    for line in open("C:/Users/jmarcano/Documents/"+sw+".txt","r"):
        interfaz.append(line.strip("\n"))
    crt.Dialog.MessageBox(str(interfaz))

def status(interfaz):
    for i in interfaz:
        crt.Screen.Send("show interface %s status\r" % i)
        crt.Screen.WaitForString("#")

def shut(interfaz):
    for i in interfaz:
        crt.Screen.Send("interface %s\r" % i)
        crt.Screen.WaitForString("#")
        crt.Screen.Send("shutdown\r")
        crt.Screen.WaitForString("#")
        crt.Screen.Send("description Disponible\r")
        crt.Screen.WaitForString("#")
    crt.Screen.Send("end\r")
    crt.Screen.Send("copy running-config startup-config\r")
    crt.Screen.Send("\r")
    crt.Screen.Synchronous = False
    crt.Sleep(20000)
    crt.Screen.Synchronous = True
    
def default(interfaz):
    for i in interfaz:
        crt.Screen.Send("default interface %s\r" % i)
        crt.Screen.WaitForString("#")

def running(interfaz):
    for i in interfaz:
        crt.Screen.Send("show running-config interface %s\r" % i)
        crt.Screen.WaitForString("#")

def description(interfaz):
    for i in interfaz:
        crt.Screen.Send("show interface %s description\r" % i)
        crt.Screen.WaitForString("#")

def clear(interfaz):
    interfaz*=0

def body():
    inter(interfaz)
    status(interfaz)
    crt.Screen.Synchronous = False
    crt.Sleep(30000)
    crt.Screen.Synchronous = True
    verificacion = crt.Dialog.Prompt("Desea proceder con el apagado de las interfaces (si/no/exit):")
    while verificacion == "no":
        clear(interfaz)
        inter(interfaz)
        status(interfaz)
        crt.Screen.Synchronous = False
        crt.Sleep(30000)
        crt.Screen.Synchronous = True
        verificacion = crt.Dialog.Prompt("Desea proceder con el apagado de las interfaces (si/no/exit):")
    if verificacion == "si":
        running(interfaz)
        crt.Screen.Send("configure terminal\r")
        crt.Screen.Synchronous = False
        crt.Sleep(1500)
        crt.Screen.Synchronous = True
        default(interfaz)
        shut(interfaz)
        description(interfaz)
        clear(interfaz)
        crt.Screen.Synchronous = False
        crt.Sleep(1500)
        crt.Screen.Send("exit\r")
        crt.Screen.Synchronous = True
    elif verificacion == "exit":
        clear(interfaz)
        crt.Screen.Send("\r")
        crt.Screen.Send("exit\r")
        crt.Screen.Send("\r")
        crt.Screen.WaitForString("#")

#Modificar el orden de los piv luego de la actividad.
try:
    cmd = "/SSH2 /L %s /PASSWORD %s %s" % (user, passwd, "1.1.1.1")
    crt.Session.Connect(cmd)
except:
    cmd = "/SSH2 /L %s /PASSWORD %s %s" % (user, passwd, "1.1.1.2")
    crt.Session.Connect(cmd)
    
for sw in SSH:
    crt.Screen.Synchronous = False
    crt.Sleep(1500)
    crt.Screen.Send("ssh -l %s %s\r" % (user, sw))
    crt.Screen.Send("%s\r" % passwd)
    crt.Screen.Synchronous = True
    crt.Screen.Send("terminal length 0\r")
    body()

for sw in Telnet:
    crt.Screen.Synchronous = False
    crt.Sleep(1500)
    crt.Screen.Send("telnet %s\r" % sw)
    crt.Screen.WaitForString("sername:")
    crt.Screen.Send("%s\r" % user)
    crt.Screen.WaitForString("assword:")
    crt.Screen.Send("%s\r" % passwd)
    crt.Screen.Synchronous = True
    crt.Screen.Send("terminal length 0\r")
    body()

crt.Session.Disconnect()