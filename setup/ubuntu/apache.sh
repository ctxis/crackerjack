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
CJ_CONFIG_APACHE="$CJ_CONFIG_FOLDER/crackerjack.conf"
CJ_APACHE_TEMPLATE="$CJ_OS_FOLDER/apache/crackerjack.conf"
CJ_APACHE_HOST="/etc/apache2/sites-enabled/crackerjack.conf"
CJ_APACHE_SSL="$CJ_CONFIG_FOLDER/ssl"

#
# Check files.
#
if [ ! -d "$CJ_CONFIG_FOLDER" ]; then
  echo "$CJ_CONFIG_FOLDER does not exist. Make sure you are running this script from the right folder."
  exit 1
elif [ ! -f "$CJ_APACHE_TEMPLATE" ]; then
  echo "$CJ_APACHE_TEMPLATE does not exist. Make sure you are running this script from the right folder."
  exit 1
fi

#
# Check for installed software.
#
APACHE=$(which apache2)
if [ -z "$APACHE" ]; then
  echo -e "apache2 server is missing. Please install using:\n"
  echo -e "sudo apt install apache2"
  echo ""
  exit 1
fi

#
# Install apache host.
#
read -r -p "Please enter the domain under which you want to install CrackerJack (ie crackerjack.local): " DOMAIN
if [ -z "$DOMAIN" ]; then
  echo "No domain given - aborting"
  exit 1
fi

#
# Generate self-signed SSL certificate.
#
openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -keyout "$CJ_APACHE_SSL.key" -out "$CJ_APACHE_SSL.crt"

ESCAPED_PATH=$(echo "$CJ_APACHE_SSL" | sed 's/\//\\\//g')
cp "$CJ_APACHE_TEMPLATE" "$CJ_CONFIG_APACHE"
sed -i "s/CJDOMAIN/$DOMAIN/g" "$CJ_CONFIG_APACHE"
sed -i "s/CJ_SSL_PATH/$ESCAPED_PATH/g" "$CJ_CONFIG_APACHE"
sudo ln -s "$CJ_CONFIG_APACHE" "$CJ_APACHE_HOST"
sudo a2enmod proxy proxy_http rewrite ssl
sudo systemctl restart apache2

# Create hashcat directory.
WWW_DATA_HOME=$(eval echo ~www-data)
if [ ! -z "$WWW_DATA_HOME" ]; then
  HASHCAT_FOLDER="$WWW_DATA_HOME/.hashcat"
  mkdir -p "$HASHCAT_FOLDER"
  sudo chown -R www-data:www-data "$HASHCAT_FOLDER"
fi

exit 0