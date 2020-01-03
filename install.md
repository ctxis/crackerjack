# Requirements

* python >= 3.6
    * In python 3.6 onwards dictionaries hold items in the same order you add them. Sounds to me this should have been the deal since version 1.
* screen >= 4.06.00
    * This version of screen onwards has the -Logfile parameter where you can set the output path of the logfile.
* hashcat
    * Any version will do, all supported hashes are dynamically extracted from the --help option.

# Installation

## Basic Software Requirement
Install basic packages using:
```
sudo apt install vim git screen python3-venv python-pip
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
```
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
flask db init
flask db migrate
flask db upgrade
deactivate
```

## Folder permissions
Within the folder, run:
```
sudo chown -R www-data:www-data ./instance ./data
```

If you have installed hashcat from source, you will need to create a ".hashcat" within the www-data user's home folder.

To identify the folder, run:

```
grep www-data /etc/passwd | awk -F':' '{ print $6 }'
```
Which will result in something like
```
/var/www
```

And then create the folder and set the right owner.
```
sudo mkdir /var/www/.hashcat
sudo chown -R www-data:www-data /var/www/.hashcat
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