#!/bin/bash


echo -e "Installing Service \n"
sudo cp moode9341-fb.service /lib/systemd/system/
sudo chmod 644 /lib/systemd/system/moode9341-fb.service
sudo systemctl daemon-reload
sudo systemctl start moode9341-fb.service
sudo systemctl status moode9341-fb.service				
echo -e "\nmoodetft-fb installed as a service.\n"
