#!/bin/bash

# Get the current script's absolute path.
CURRENT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
CJ_PATH=$(cd "$CURRENT_PATH/../" && pwd)

#
# First check if required software is installed
#
SCREEN=$(which screen)
SCREEN_REQUIRED_VERSION="4.06.00"

PYTHON=$(which python3)
PYTHON_REQUIRED_VERSION="3.6.0"

PIP=$(which pip)

if [ -z "$SCREEN" ]; then
  echo -e "The screen application is missing. Please install using:\n"
  echo -e "sudo apt install screen"
  echo ""
  exit 1
elif [ -z "$PYTHON" ]; then
  echo -e "python3 is missing - make sure you install python >= 3.6"
  exit 1
elif [ -z "$PIP" ]; then
  echo -e "pip is missing. Please install using:\n"
  echo -e "sudo apt install python-pip"
  echo ""
  exit 1
fi

#
# Now check the versions of that software
#
SCREEN_VERSION=$("$SCREEN" --version | awk -F' ' '{ print $3 }')
if [ ! "$(printf '%s\n' "$SCREEN_REQUIRED_VERSION" "$SCREEN_VERSION" | sort -V | head -n1)" = "$SCREEN_REQUIRED_VERSION" ]; then
  echo "screen version has to be at least $SCREEN_REQUIRED_VERSION but version $SCREEN_VERSION was identified"
  exit 1
fi

PYTHON_VERSION=$("$PYTHON" --version | awk -F' ' '{ print $2 }')
if [ ! "$(printf '%s\n' "$PYTHON_REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$PYTHON_REQUIRED_VERSION" ]; then
  echo "python3 version has to be at least $PYTHON_REQUIRED_VERSION but version $PYTHON_VERSION was identified"
  exit 1
fi

# Create venv.
cd "$CJ_PATH" || exit 1

"$PYTHON" -m venv venv

# Activate.
. venv/bin/activate

# Install requirements.
cd "$CJ_PATH" && "$PIP" install -r requirements.txt

# Install Flask database.
flask db init
flask db migrate
flask db upgrade

# Deactivate.
deactivate

cd "$CURRENT_PATH" || exit 1

# Set the right permissions.
sudo chown -R www-data:www-data "$CJ_PATH/instance" "$CJ_PATH/data"

echo "CJ Installation Complete."

exit 0
