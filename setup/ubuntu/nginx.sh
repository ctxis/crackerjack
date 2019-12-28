#!/bin/bash

#
# Make sure we can execute sudo commands
#
echo "This script will need to run some sudo commands, please enter your sudo password below to ensure you have the right permissions:"
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
CJ_CONFIG_NGINX="$CJ_CONFIG_FOLDER/crackerjack"
CJ_NGINX_TEMPLATE="$CJ_OS_FOLDER/nginx/crackerjack.conf"
CJ_NGINX_HOST="/etc/nginx/sites-enabled/crackerjack"
CJ_NGINX_SSL="$CJ_CONFIG_FOLDER/ssl"

#
# Check files.
#
if [ ! -d "$CJ_CONFIG_FOLDER" ]; then
  echo "$CJ_CONFIG_FOLDER does not exist. Make sure you are running this script from the right folder."
  exit 1
elif [ ! -f "$CJ_NGINX_TEMPLATE" ]; then
  echo "$CJ_NGINX_TEMPLATE does not exist. Make sure you are running this script from the right folder."
  exit 1
fi

#
# Check for installed software.
#
NGINX=$(which nginx)
if [ -z "$NGINX" ]; then
  echo -e "nginx server is missing. Please install using:\n"
  echo -e "sudo apt install nginx"
  echo ""
  exit 1
fi

#
# Install nginx host.
#
read -r -p "Please enter the domain under which you want to install CrackerJack (ie crackerjack.local): " DOMAIN
if [ -z "$DOMAIN" ]; then
  echo "No domain given - aborting"
  exit 1
fi

#
# Generate self-signed SSL certificate.
#
openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -keyout "$CJ_NGINX_SSL.key" -out "$CJ_NGINX_SSL.crt"

ESCAPED_PATH=$(echo "$CJ_NGINX_SSL" | sed 's/\//\\\//g')
cp "$CJ_NGINX_TEMPLATE" "$CJ_CONFIG_NGINX"
sed -i "s/CJDOMAIN/$DOMAIN/g" "$CJ_CONFIG_NGINX"
sed -i "s/CJ_SSL_PATH/$ESCAPED_PATH/g" "$CJ_CONFIG_NGINX"
sudo ln -s "$CJ_CONFIG_NGINX" "$CJ_NGINX_HOST"
sudo systemctl restart nginx

exit 0