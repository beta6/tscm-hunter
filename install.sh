#!/bin/bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip rtl-sdr sox libsox-fmt-all iw wireless-tools bluez
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
echo installed
