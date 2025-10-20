# Listener V3 — Professional Reverse Shell Listener

**WARNING — FOR LAB USE ONLY**

This repository contains `Listener_V3.py`, a professional-grade reverse shell listener intended for use in controlled laboratory environments, training, and authorized red-team exercises. This software is **not** designed for or authorized for use on systems for which you do not have explicit permission. Misuse may be illegal and unethical.

---

## Overview

`Listener_V3` is a polished and operator-friendly reverse shell listener written in Python 3. It focuses on reliable interactive sessions, multi-client management, and a clear operator UX. The listener collects command output without requiring an explicit end-of-output marker by using non-blocking reads and short idle detection windows.

Key features

* Colorful and concise terminal UI (powered by `colorama`).
* Multi-client support (one handler thread per client).
* No end-marker protocol (collects output via non-blocking I/O and select).
* Optional pre-shared-token authentication (suitable for lab environments).
* Rotating file logging to keep operational logs bounded.
* Operator commands: `clients`, `select <id>`, `broadcast <cmd>`, `help`, `clear`, `exit`.

---

## Requirements

* Python 3.8 or later.
* Python package: `colorama`.

Install dependencies using `pip`:

```bash
pip install colorama
```

---

## Quick Start

1. Place `Listener_V3.py` in your working directory.
2. Run the listener (default: binds to `0.0.0.0:4444`):

```bash
python3 Listener_V3.py --host 0.0.0.0 --port 4444
```

3. (Optional) Disable token authentication for quick testing (only in closed labs):

```bash
python3 Listener_V3.py --no-auth
```

4. On a cooperating client machine, run a compatible client that connects to the listener and executes received commands. A sample client script is provided in this project (or can be created to match the listener's expected behavior).

---

## Usage and Operator Commands

Once the server is running, the operator is presented with a prompt `server>` and may use the following commands:

* `help` — Display help text and available commands.
* `clients` — Show a numbered list of connected clients (ID, IP:port, status, uptime).
* `select <id>` — Select a client session for interaction. All subsequent commands are sent to that client.
* `broadcast <command>` — Send a command to all currently connected clients and display their outputs.
* `clear` — Clear the operator console screen.
* `info` — Show server status and basic metrics.
* `exit` / `quit` — Shutdown the listener and close all connections.

Example interactive session:

```text
server> clients
[Clients]
 # 1  10.10.10.20:53832    alive    connected 12s
server> select 1
Selected client #1 -> 10.10.10.20:53832
server> whoami
────────────────────────────────────────────────────────
> OUTPUT — 2025-10-20 15:12:15
  root
────────────────────────────────────────────────────────
```

---

## Client Requirements and Notes

A cooperating client must:

* Connect to the listener's TCP socket.
* Optionally respond to the `TOKEN?` prompt with the pre-shared token (if auth is enabled).
* Read command lines sent by the listener (terminated by `\n`).
* Execute the received commands in a local shell and send back `stdout` and `stderr` as raw bytes.

**Important:** The server does not rely on an explicit end-of-output marker. Clients should send output in full and allow the server's idle-detection window to collect it. The sample client included with the project demonstrates the recommended behavior.

---

## Logging

Operational logs are written to a rotating log file (`listener_v3.log` by default). The log captures connection events, errors, authentication attempts, and unsolicited client data. Log rotation is configured to preserve disk space.

---

## Security and Legal Notice

This code is intended strictly for use in environments where you have explicit authorization (e.g., lab networks, penetration testing engagements with written permission, or educational demonstrations). Unauthorized use against systems you do not own or have permission to test is illegal and unethical.

If you plan to use this tool in a sensitive environment, consider the following hardening steps:

* Wrap the TCP connection in TLS (use `ssl.wrap_socket`) and validate certificates.
* Replace pre-shared token auth with mutual TLS or an authenticated tunnel (SSH/VPN).
* Run the listener and clients over isolated networks or VLANs during experiments.
* Keep logging and monitoring active; limit filesystem and log access to authorized operators.

---

## Deployment and Integration Guidance

* Place `Listener_V3.py` under version control and maintain a changelog.
* Use a separate branch for experimental changes; create a pull request to merge to the canonical branch.
* If you plan to run the listener persistently on a controlled host, consider running it under a process supervisor (e.g., `systemd` or `supervisord`) and configure appropriate restart policies and resource limits.

---

## Contributing

Contributions are welcome from authorized project collaborators. Follow standard Git workflows:

1. Fork the repository.
2. Create a descriptive branch (e.g., `feature/auto-reconnect-client`).
3. Make small, focused commits with meaningful messages.
4. Open a Pull Request and include tests or usage notes for new behavior.

Note: Maintain strict control over features that increase the risk of misuse.

---

## License

This project does not include a license by default. If you intend to share this code publicly, add an appropriate license file (for example, an MIT or Apache 2.0 license) and ensure that the legal terms are compatible with your intended usage.

---

## Contact and Support

For assistance with integration or adapting the listener for your lab, open an issue in the repository or contact the project maintainer. Include your environment details (OS, Python version) and a short description of the problem.

---

## Change Log (high level)

* **v3** — Professional UI, multi-client support, no end-marker, rotating logs, optional token auth.

---

*Prepared for controlled laboratory use. Do not use on unauthorized systems.*
