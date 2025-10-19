# 🐍 Webixly Reverse Shell — Educational Cybersecurity Project

> ⚠️ **Disclaimer:**  
> This project is created **for educational and ethical learning purposes only**.  
> Do **not** use it against any system or network without explicit authorization.  
> Unauthorized use of this code may violate local and international laws.

---

## 📘 Overview

This project demonstrates the **concept of a Reverse Shell** in a safe and controlled way.  
It aims to help cybersecurity students and enthusiasts **understand how reverse shells work** — and more importantly, **how to defend against them**.

A reverse shell is a type of connection where the target (client) initiates a connection **back to an attacker’s server**, allowing remote command execution.  
While often used in penetration testing, this mechanism can also be abused by attackers.

---

## ⚙️ Project Structure

This repository contains two main components:

1. **`server.py`** – The command dispatcher  
   - Listens for incoming client connections.  
   - Executes **only safe, predefined commands** (no OS-level commands).  
   - Returns structured JSON responses.

2. **`client.py`** – The simulated client  
   - Connects to the server using sockets.  
   - Sends JSON-formatted commands such as:
     - `hello` → returns a greeting  
     - `time` → returns the current UTC time  
     - `sysinfo` → returns system information  

This simulation helps you learn the logic of reverse communication without any malicious behavior.

---

## 🔍 How a Reverse Shell Works (Conceptually)

1. Normally, a server waits for connections from clients.  
2. In a **reverse shell**, the client (target) initiates the connection to the server (attacker).  
3. Once connected, commands can be exchanged over that channel.  
4. In this educational version, only *safe* commands are executed — no real shell commands.

---

## 🛡️ How to Protect Systems from Reverse Shells

- 🔒 **Use firewalls** to block outgoing connections to unknown IPs and ports.  
- 🧩 **Monitor network traffic** for suspicious or unexpected connections.  
- 🚫 **Restrict or sandbox** applications that can execute shell commands.  
- 🧑‍💻 **Audit code and scripts** for any unsafe socket or subprocess usage.  
- 🧰 **Deploy EDR/NDR tools** to detect unusual connection patterns.

---

## 🧪 Running the Project (Safe Environment Only)

```bash
# Run the server (listener)
python3 server.py

# On another device or terminal (same network):
python3 client.py
