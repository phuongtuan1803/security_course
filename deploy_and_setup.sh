#!/bin/bash

# Import config.sh
source ./config.sh

# Copy client.sh to remote via SSH (port 2202)
scp -i ./.vagrant/machines/pc1/virtualbox/private_key -P 2202 config.sh vagrant@127.0.0.1:~/config.sh
scp -i ./.vagrant/machines/pc1/virtualbox/private_key -P 2202 client.sh vagrant@127.0.0.1:~/client.sh

# Copy server.sh to remote via SSH (port 2222)
scp -i ./.vagrant/machines/pc2/virtualbox/private_key -P 2222 config.sh vagrant@127.0.0.1:~/config.sh
scp -i ./.vagrant/machines/pc2/virtualbox/private_key -P 2222 server.sh vagrant@127.0.0.1:~/server.sh

# Run ssh-keygen on remote via SSH (port 2200), auto-overwrite existing key
# ssh -i ./.vagrant/machines/pc0/virtualbox/private_key -p 2201 vagrant@127.0.0.1 "yes | ssh-keygen -q -N '' -f ~/.ssh/id_rsa"
ssh -i ./.vagrant/machines/pc0/virtualbox/private_key -p 2201 vagrant@127.0.0.1 "git config --global user.name "phuongtuan" && git config --global user.email "phuongtuan1803@gmail.com""
ssh -i ./.vagrant/machines/pc0/virtualbox/private_key -p 2201 vagrant@127.0.0.1 "cat ~/.ssh/id_rsa.pub"