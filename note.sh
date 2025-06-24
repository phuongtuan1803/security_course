sudo dhclient -r eth1  # Release IP hiện tại
sudo dhclient eth1     # Yêu cầu cấp lại IP từ DHCP

sudo dhclient -r enp0s8
sudo dhclient enp0s8 

sudo ip -s -s neigh flush all
sudo arp -a

sudo netplan apply

sudo ip addr del 172.20.3.89/24 dev eth1
sudo ip addr add 172.20.0.1/24 dev eth1
sudo ip route add default via 172.20.3.1 dev eth1 # Hyatt
sudo systemctl restart NetworkManager


# Gán IP nếu cần (nếu chưa có)
sudo ip addr add 172.20.3.89/20 dev eth1

# Xoá default route cũ (nếu có)
sudo ip route del default

# Gán gateway đúng
sudo ip route add default via 172.20.0.1 dev eth1

# Kiểm tra lại
ip route
ping -c 3 8.8.8.8