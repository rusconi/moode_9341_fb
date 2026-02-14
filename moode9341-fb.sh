#!/bin/bash

# moodetft-fb
# v0.001 
 
while getopts ":sq" opt; do
  case ${opt} in
    s ) sudo pkill -f fbup.py; 
        sudo /usr/bin/python3 /home/pi/moodetft-fb/clear_tftfb.py; 
        sudo /usr/bin/python3 /home/pi/moodetft-fb/fbup.py &
      ;;
    q ) sudo pkill -f fbup.py; 
        sudo python3 /home/pi/moodetft-fb/clear_tftfb.py
      ;;
    \? ) echo "Usage: cmd [-s] [-q]"
      ;;
  esac
done