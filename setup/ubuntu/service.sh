#!/bin/bash

#
# Make sure we can execute sudo commands
#
echo "This script will need to run some sudo commands, please enter your sudo password below to ensure you have the right permimssions:"
SUDO=$(sudo whoami)
if [ -z "$SUDO" ]; then
  echo "Invalid SUDO credentials - aborting"
  exit 1
fi

# Get the current script's absolute path.
CURRENT_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
CJ_PATH=$(cd "$CURRENT_PATH/../../" && pwd)

CJ_OS_FOLDER="$CJ_PATH/os"
CJ_CONFIG_FOLDER="$CJ_OS_FOLDER/config"
CJ_CONFIG_SERVICE="$CJ_CONFIG_FOLDER/crackerjack.service"
CJ_SYSTEMD_SERVICE="/etc/systemd/system/crackerjack.service"
CJ_SERVICE_TEMPLATE="$CJ_OS_FOLDER/ubuntu/crackerjack.service"

#
# Check files.
#
if [ ! -d "$CJ_CONFIG_FOLDER" ]; then
  echo "$CJ_CONFIG_FOLDER does not exist. Make sure you are running this script from the right folder."
  exit 1
elif [ ! -f "$CJ_SERVICE_TEMPLATE" ]; then
  echo "$CJ_SERVICE_TEMPLATE does not exist. Make sure you are running this script from the right folder."
  exit 1
fi

#
# Install service
#
ESCAPED_PATH=$(echo "$CJ_PATH" | sed 's/\//\\\//g')
cp "$CJ_SERVICE_TEMPLATE" "$CJ_CONFIG_SERVICE"
sed -i "s/CJPATH/$ESCAPED_PATH/g" "$CJ_CONFIG_SERVICE"

sudo ln -s "$CJ_CONFIG_SERVICE" "$CJ_SYSTEMD_SERVICE"
sudo systemctl start crackerjack.service
sudo systemctl status crackerjack.service

exit 0