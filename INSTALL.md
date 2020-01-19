# Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
  - [Base Software](#base-software-requirement)
  - [Clone Repository](#clone-repo)
  - [Virtual Environment](#virtual-environment)
    - [Permissions](#virtual-environment-permissions)
    - [Crontab](#install-crontab)
  - System Configuration
    - [Install Service](#install-systemd-service)
    - Web Server Setup
      - [nginx](#install-nginx-host)
      - [apache2](#install-apache2-host)
- [Third Party Software](#third-party-software)
  - [Screen](#screen)
    - [Compile](#compile)
  - [Hashcat](#hashcat)
- [Configuration](#crackerjack-configuration)
- [Run Locally](#run-locally)

# Requirements

* python >= 3.6
    * In python 3.6 onwards dictionaries hold items in the same order you add them. Sounds to me this should have been the deal since version 1.
* screen >= 4.06.00
    * This version of screen onwards has the -Logfile parameter where you can set the output path of the logfile.
* hashcat
    * Any version will do, all supported hashes are dynamically extracted from the --help option.

# Installation

## Base Software Requirement
Install basic packages using:
```
sudo apt install vim git screen python3-venv python-pip sqlite3
```

If you want to use nginx:
```
sudo apt install nginx
```
And if you are an Apache fan:
```
sudo apt install apache2
```

## Clone Repo

```
git clone [[this-repo]]
```

## Virtual Environment
Navigate to the path you cloned crackerjack into, and run the following commands:

```
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
flask db init
flask db migrate
flask db upgrade
deactivate
```

## Virtual Environment Permissions
As the web server will be running under www-data, the application should be owned by that user.
```
sudo chown -R www-data:www-data /path/to/crackerjack
```

If you have installed hashcat from source, you will need to create a ".hashcat" within the www-data user's home folder.

To identify the folder, run:

```
eval echo ~www-data
```
Which will result in something like
```
/var/www
```
If `/var/www` doesn't exist it means that neither nginx or apache are installed.

Now create the folder and set the right owner.
```
sudo mkdir /var/www/.hashcat

or

sudo mkdir $(eval echo ~www-data)/.hashcat
```
Set permissions
```
sudo chown -R www-data:www-data /var/www/.hashcat
```

### Install Crontab

This functionality is required to auto-terminate jobs when they exceed their allowed run time, and for general housekeeping.

Navigate to CrackerJack and run the following:

```
sudo -u www-data /bin/bash  # Login as www-data before executing the following commands.
. venv/bin/activate
flask crontab add
deactivate
```

Confirm that the job has been added by running:
```
crontab -l
```

## Install systemd service
Run
```
./setup/ubuntu/service.sh
```
This will create the "crackerjack.service" and its config file will be located at:
```
./os/config/crackerjack.service
```
To control the service use:
```
sudo systemctl start|stop|disable crackerjack.service
```

## Install nginx host
If you are running nginx, run
```
./setup/ubuntu/nginx.sh
```
This will create the "crackerjack" host which will proxy all its traffic to the systemd service created above. The nginx config file will be at:
```
./os/config/crackerjack
```
This option will also generated a self-signed certificate which will be located in the same folder - feel free to replace it.

## Install apache2 host
If you are running apache2, run
```
./setup/ubuntu/apache.sh
```
This will create the "crackerjack" host which will proxy all its traffic to the systemd service created above. The apache config file will be at:
```
./os/config/crackerjack.conf
```
This option will also generated a self-signed certificate which will be located in the same folder - feel free to replace it.

# Third-party Software

## Screen

If you are running a linux distribution that doesn't have the latest version in its repos, you can download and compile it from source.

### Packages
```
sudo apt install libncurses5-dev
```

### Compile
```
cd ~
wget http://ftp.gnu.org/gnu/screen/screen-4.7.0.tar.gz -O screen.tar.gz
tar -xf screen.tar.gz
cd ./screen-4.7.0
./configure
make
sudo make install
```

### Check version
```
$ screen --version
Screen version 4.07.00 (GNU) 02-Oct-19
```

## Hashcat

It's recommended to compile hashcat from source - instructions are at https://github.com/hashcat/hashcat/blob/master/BUILD.md

# CrackerJack Configuration

To set your own Flask configuration:
 
Copy `config.py` from `./setup/config.py` to `./instance/config.py`

# Run Locally

You can also run CrackerJack locally without using Apache/nginx:

```
git clone [[this-repo]]
```

Navigate inside the cloned directory and run:

```
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
flask db init
flask db migrate
flask db upgrade

export FLASK_ENV=development
export FLASK_APP=app
flask run
```

After the last command you should see something like:

```
(venv) $ flask run
 * Serving Flask app "app" (lazy loading)
 * Environment: development
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 182-315-751
```

To access CrackerJack navigate to `http://127.0.0.1:5000/` 