#!/bin/bash

echo "Would you like to install service (Y/N)?"
read response

if [[ "$response" == "Y" ]]; then
 
    echo -e "Installing Service \n"
    set -x
    sudo cp moode9341-fb.service /lib/systemd/system/
    sudo chmod 644 /lib/systemd/system/moode9341-fb.service
    sudo systemctl enable moode9341-fb.service
    sudo systemctl daemon-reload
    sudo systemctl start moode9341-fb.service
    sudo systemctl status moode9341-fb.service				
    echo -e "\nmoodetft-fb installed as a service.\n"

else
    echo "service not installed!"
fi