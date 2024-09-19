#!/bin/bash

sudo apt update
sudo apt install python3-pip
pip install paramiko
python3 command_server.py