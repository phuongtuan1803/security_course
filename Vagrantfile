# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.boot_timeout = 600

  # Host's network adapter to use for the bridge.
  # Change this adapter name to match your host machine.
  $bridge_interface = "Intel(R) Wi-Fi 6E AX211 160MHz"

  # ---------- PC1 (Ubuntu) ----------
  config.vm.define "pc1" do |pc1|
    pc1.vm.box = "ubuntu/focal64"

    # Configure Bridge Mode
    pc1.vm.network "public_network",
                      bridge: $bridge_interface,
                      use_dhcp_assigned_default_route: true,
                      mac: "AABBCCDD0001",
                      promiscuous_mode: "allow-all"

    pc1.vm.provider "virtualbox" do |vb|
      vb.gui = false
      vb.memory = "1024"
      vb.cpus   = "1"
      # Enable Promiscuous mode so the NIC can capture all network traffic
      vb.customize ["modifyvm", :id, "--nicpromisc2", "allow-all"]
    end
  end

  # ---------- PC2 (Ubuntu) ----------
  config.vm.define "pc2" do |pc2|
    pc2.vm.box = "ubuntu/focal64"

    # Configure Bridge Mode
    pc2.vm.network "public_network",
                      bridge: $bridge_interface,
                      use_dhcp_assigned_default_route: true,
                      mac: "AABBCCDD0002",
                      promiscuous_mode: "allow-all"

    pc2.vm.provider "virtualbox" do |vb|
      vb.gui = false
      vb.memory = "1024"
      vb.cpus   = "1"
      vb.customize ["modifyvm", :id, "--nicpromisc2", "allow-all"]
    end
  end

  # ────────── kali (Bridge Mode) ──────────
  config.vm.define "kali" do |kali|
    kali.vm.box = "kalilinux/rolling"
    
    # Configure Bridge Mode, allowing kali to get an IP directly from the physical router
    kali.vm.network "public_network",
                      bridge: $bridge_interface,
                      use_dhcp_assigned_default_route: true,
                      mac: "AABBCCDD0000",
                      promiscuous_mode: "allow-all"
                

    kali.vm.provider "virtualbox" do |vb|
      vb.gui = false
      vb.memory = "2048"
      vb.cpus   = "2"
      vb.customize ["modifyvm", :id, "--nicpromisc2", "allow-all"]
    end

    # Provisioning block to install necessary packages
    kali.vm.provision "shell", inline: <<-SHELL
      wget https://http.kali.org/kali/pool/main/k/kali-archive-keyring/kali-archive-keyring_2025.1_all.deb
      sudo dpkg -i kali-archive-keyring_2025.1_all.deb
      sudo apt update -y
      sudo apt install isc-dhcp-client

      # for arp spoofing
      sudo apt install bettercap -y
      sudo apt install libnfnetlink-dev libnetfilter-queue-dev
      sudo apt install libmnl-dev libpcap-dev -y
      sudo python3 -m pip install --break-system-packages netfilterqueue

      # for flight data
      python -m pip install pyModeS --break-system-packages
      python3 -m pip install --upgrade ads-b --break-system-packages
      sudo apt install -y librtlsdr-dev pkg-config build-essential libusb-1.0-0-dev



    SHELL
    # sudo apt-get update -y
    # sudo apt-get install -y isc-dhcp-client
    # 
    # Try to fix before destroy

  end
end