#!/bin/bash

echo -e "Install moodetft-fb. \n"

# install required libraries
while true
do
    read -p "Do you wish to install the required libraries [y/n]?" yn
    case $yn in
        [Yy]* ) sudo apt-get update
                echo -e "Installing Libraries... \n"
                sudo apt-get install python3-rpi.gpio python3-spidev python3-pip python3-pil python3-numpy python3-gpiozero python3-pigpio libatlas-base-dev

                sudo pip3 install mediafile watchgod

                echo -e "Libraries installed. \n"
                break;;
        [Nn]* ) echo -e "Libraries not installed \n"; break;;
        * ) echo "Please answer yes[y] or no[n].";;
    esac
done


# install service
while true
do
    read -p "Do you wish to install MoodeTFT-FB as a service [y/n]?" yn
    case $yn in
        [Yy]* ) echo -e "Installing Service \n"
                sudo cp moodetft-fb.service /lib/systemd/system
                sudo chmod 644 /lib/systemd/system/moodetft-fb.service
                sudo systemctl daemon-reload
                sudo systemctl enable moodetft-fb.service
				echo -e "\nmoodetft-fb installed as a service.\n"
                echo -e "Please reboot the Raspberry Pi.\n"
                break;;
        [Nn]* ) echo -e "Service not installed \n"; break;;
        * ) echo "Please answer yes[y] or no[n].";;
    esac
done

# reboot now?
while true
do
    read -p "Do you wish to reboot now [y/n]?" yn
    case $yn in
        [Yy]* ) echo -e "Rebooting \n"
                sudo reboot
                break;;
        [Nn]* ) echo -e "Not rebooting \n"
                break;;
        * ) echo "Please answer yes[y] or no[n].";;
    esac
done

echo "MoodeTFT-FB install complete"
