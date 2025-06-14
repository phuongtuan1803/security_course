#!/bin/bash

get_ssh_port() {
  local vm_name="$1"

  if [[ -z "$vm_name" ]]; then
    echo "VM name is required." >&2
    return 1
  fi

  # Lấy SSH host port của VM (forward từ guest 22)
  local port
  port=$(vagrant port "$vm_name" --guest 22 2>/dev/null)

  if [[ -z "$port" ]]; then
    echo "Could not retrieve SSH port for VM: $vm_name" >&2
    return 2
  fi

  echo "$port"
}
vagrant up pc1
# Copy client.sh to remote via SSH (port 2202)
vm="pc1"
ssh_port=$(get_ssh_port "$vm") || exit 1

scp -i ./.vagrant/machines/pc1/virtualbox/private_key -P $ssh_port vm_setup/config.sh vagrant@127.0.0.1:~/config.sh
scp -i ./.vagrant/machines/pc1/virtualbox/private_key -P $ssh_port vm_setup/client.sh vagrant@127.0.0.1:~/client.sh

# Copy server.sh to remote via SSH (port 2222)
vm="pc2"
ssh_port=$(get_ssh_port "$vm") || exit 1
scp -i ./.vagrant/machines/pc2/virtualbox/private_key -P $ssh_port vm_setup/config.sh vagrant@127.0.0.1:~/config.sh
scp -i ./.vagrant/machines/pc2/virtualbox/private_key -P $ssh_port vm_setup/server.sh vagrant@127.0.0.1:~/server.sh

# Run ssh-keygen on remote via SSH (port 2200), auto-overwrite existing key
vm="kali"
ssh_port=$(get_ssh_port "$vm") || exit 1
ssh -i ./.vagrant/machines/kali/virtualbox/private_key -p $ssh_port vagrant@127.0.0.1 "git config --global user.name "phuongtuan" && git config --global user.email "phuongtuan1803@gmail.com""
scp -i ./.vagrant/machines/kali/virtualbox/private_key -P $ssh_port vm_setup/id_ed25519 vagrant@127.0.0.1:~/.ssh/id_ed25519
scp -i ./.vagrant/machines/kali/virtualbox/private_key -P $ssh_port vm_setup/id_ed25519.pub vagrant@127.0.0.1:~/.ssh/id_ed25519.pub
ssh -i ./.vagrant/machines/kali/virtualbox/private_key -p $ssh_port vagrant@127.0.0.1 "git clone git@github.com:phuongtuan1803/security_course.git"
