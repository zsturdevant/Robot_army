#!/bin/bash

sudo apt update
sudo apt install python3-pip
pip install paramiko
pip install requests
sudo apt install openssh-client
sudo apt install openssh-server
sudo sshd -t -f /etc/ssh/sshd_config
python3 bot.py