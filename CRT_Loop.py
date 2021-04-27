import os
os.chdir("C:/Users/jmarcano/Documents")

crt.Screen.Synchronous = True
user = crt.Dialog.Prompt("Enter user for SSH:")
passwd = crt.Dialog.Prompt("Enter password:")
SW = []
comandos = []
fp = open("validacion_CRT.txt", "w+")
try:
    cmd = "/SSH2 /L %s /PASSWORD %s %s" % (user, passwd, pivotes.get("piv2"))
    crt.Session.Connect(cmd)
except:
    cmd = "/SSH2 /L %s /PASSWORD %s %s" % (user, passwd, pivotes.get("piv"))
    crt.Session.Connect(cmd)
def loop():
    for c in comandos:
        crt.Screen.Send("%s\r" % c)
    crt.Screen.Send("###\r")
    fp.write(crt.Screen.ReadString(["####", "# ###"]))

for i in SW:
    #fp = open(i+".txt", "w+")
    #Telnet
    if i == '1.1.1.1':
        crt.Screen.Send("telnet %s \r" % i)
        crt.Screen.WaitForString("sername:")
        crt.Screen.Send("%s\r" % user)
        crt.Screen.WaitForString("assword:")
        crt.Screen.Send("%s\r" % passwd)
        crt.Screen.Synchronous = True
        loop()
        crt.Screen.Synchronous = False
        crt.Sleep(1500)
        crt.Screen.Send("exit\r")
        crt.Sleep(500)
    #SSH
    elif i != '1.1.1.1':
        crt.Screen.Send("ssh -l %s %s\r" % (user, i))
        crt.Screen.Send("%s\r" % passwd)
        crt.Screen.Synchronous = True
        loop()
        crt.Screen.Synchronous = False
        crt.Sleep(1500)
        crt.Screen.Send("exit\r")
        crt.Sleep(500)
#Desconexion del pivote
fp.close()
crt.Sleep(500)
crt.Session.Disconnect()