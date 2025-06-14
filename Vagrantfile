# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/focal64"
  config.vm.boot_timeout = 600 

  # ---------- PC1 ----------
  config.vm.define "pc1" do |pc1|
    pc1.vm.network "public_network",
                   bridge: "Intel(R) Wi-Fi 6E AX211 160MHz",
                   use_dhcp_assigned_default_route: true,
                   promiscuous_mode: "allow-all"

    pc1.vm.provider "virtualbox" do |vb|
      vb.gui = false
      vb.memory = "1024"
      vb.cpus   = "1"
      vb.customize ["modifyvm", :id, "--hwvirtex", "on"]
      vb.customize ["modifyvm", :id, "--nested-paging", "on"]
      vb.customize ["modifyvm", :id, "--nicpromisc1", "allow-all"]
    end
  end

  # ---------- PC2 ----------
  config.vm.define "pc2" do |pc2|
    pc2.vm.network "public_network",
                   bridge: "Intel(R) Wi-Fi 6E AX211 160MHz",
                   use_dhcp_assigned_default_route: true,
                   promiscuous_mode: "allow-all"

    pc2.vm.provider "virtualbox" do |vb|
      vb.gui = false
      vb.memory = "1024"
      vb.cpus   = "1"
      vb.customize ["modifyvm", :id, "--hwvirtex", "on"]
      vb.customize ["modifyvm", :id, "--nested-paging", "on"]
      vb.customize ["modifyvm", :id, "--nicpromisc1", "allow-all"]
    end
  end

  # ────────── Kali (NAT) ──────────
  config.vm.define "kali" do |kali|
    kali.vm.box = "kalilinux/rolling"    

    kali.vm.network "public_network",
                   bridge: "Intel(R) Wi-Fi 6E AX211 160MHz",
                   use_dhcp_assigned_default_route: true,
                   promiscuous_mode: "allow-all"

    kali.vm.provider "virtualbox" do |vb|
      vb.gui = false
      vb.memory = "2048"            
      vb.cpus   = "2"
      vb.customize ["modifyvm", :id, "--hwvirtex", "on"]
      vb.customize ["modifyvm", :id, "--nested-paging", "on"]
      vb.customize ["modifyvm", :id, "--nicpromisc1", "allow-all"]
    end

    kali.vm.provision "shell", inline: <<-SHELL
      sudo apt-get update -y
      sudo apt-get dist-upgrade -y
    SHELL
  end
end
