sudo dhclient -r eth1  # Release IP hiện tại
sudo dhclient eth1     # Yêu cầu cấp lại IP từ DHCP

sudo dhclient -r enp0s8
sudo dhclient enp0s8 

sudo ip -s -s neigh flush all
sudo arp -a

sudo netplan apply


sudo ip addr add 172.20.3.89/24 dev eth1
sudo ip addr del 172.20.3.89/24 dev eth1
sudo systemctl restart NetworkManager
