import os
os.chdir("C:/Users/jmarcano/Documents/Python")

crt.Screen.Synchronous = True
user = crt.Dialog.Prompt("Enter user for SSH:")
passwd = crt.Dialog.Prompt("Enter password:")
pivotes = {"piv":"172.22.1.1","piv2":"172.22.2.1"}
SW = []
comandos = ["terminal length 0"]
for ip in open("IP_validacion.txt"):
    SW.append(ip.strip("\n"))
fp = open("validacion_CRT.txt", "w+")
try:
    cmd = "/SSH2 /L %s /PASSWORD %s %s" % (user, passwd, pivotes.get("piv"))
    crt.Session.Connect(cmd)
except:
    cmd = "/SSH2 /L %s /PASSWORD %s %s" % (user, passwd, pivotes.get("piv2"))
    crt.Session.Connect(cmd)
def loop():
    for command in comandos:
        crt.Screen.Send("%s\r" % command)
    crt.Screen.Send("####\r")
    fp.write(crt.Screen.ReadString(["####", "# ###"]))

for sw in SW:
    #fp = open(i+".txt", "w+")
    #Telnet
    if sw == '1.1.1.1':
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
    elif sw != '1.1.1.1':
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