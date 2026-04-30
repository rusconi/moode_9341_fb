#!/bin/bash

# Service name
SERVICE="moode9341-fb.service"

# Check if script is run as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root (use sudo)" 
   exit 1
fi

echo "Stopping $SERVICE..."
systemctl stop "$SERVICE"

echo "Disabling $SERVICE..."
systemctl disable "$SERVICE"

# Define common service locations
SERVICE_PATH="/etc/systemd/system/$SERVICE"
LIB_PATH="/lib/systemd/system/$SERVICE"

echo "Removing service files..."
if [ -f "$SERVICE_PATH" ]; then
    rm "$SERVICE_PATH"
    echo "Removed $SERVICE_PATH"
fi

if [ -f "$LIB_PATH" ]; then
    rm "$LIB_PATH"
    echo "Removed $LIB_PATH"
fi

echo "Reloading systemd daemon..."
systemctl daemon-reload
systemctl reset-failed

echo "$SERVICE has been stopped and removed."
