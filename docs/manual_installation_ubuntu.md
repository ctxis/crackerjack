# CrackerJack / Ubuntu Installation

* [Environment](#environment)
* [CrackerJack](#crackerjack)
  * [Clone Source Code](#clone-source-code)
  * [Virtual Environment](#virtual-environment)
    * [Permissions](#virtual-environment-permissions)
    * [Crontab](#crontab)
  * [Run Locally](#run-locally)
  * [Configuration](#crackerjack-configuration)
* [System Service](#system-service)
  * [Service Variables](#service-variables)
  * [systemd](#systemd)
  * [init.d](#initd)
* [Web Server](#web-server)
  * [Virtual Host Variables](#virtual-host-variables)
  * [SSL Certificates](#ssl-certificates)
  * [Apache](#apache)
  * [nginx](#nginx)
* [.hashcat Directory](#hashcat-directory)
  
# Environment

Install required packages:

16.04 / 18.04
```
sudo apt install git screen python3-venv python3-pip sqlite3
```

14.04 (Python 3.6 is not installed by default, make sure you install it before you proceed)
```
sudo apt install git screen python3.6-venv python3-pip sqlite3
```

# CrackerJack

## Clone Source Code

```
git clone https://github.com/ctxis/crackerjack
```

## Virtual Environment

Navigate to the path you cloned crackerjack into, and run the following commands:

```
python3 -m venv venv    # You might need to change python3 to python3.6
. venv/bin/activate
pip install -r requirements.txt
flask db init
flask db migrate
flask db upgrade
deactivate
```

At this point you can run CrackerJack locally by following the instructions [here](#run-locally).

### Virtual Environment Permissions

#### Set owner to www-data

As the web server will be running under www-data, the application should be owned by that user.
```
sudo chown -R www-data:www-data /path/to/crackerjack
```

### Crontab

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

## Run Locally

You can also run CrackerJack locally without using Apache/nginx. Navigate inside the cloned directory and run (make sure you have installed the virtual environment following the instructions [here](#virtual-environment)):

```
. venv/bin/activate
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

## CrackerJack Configuration

The first-time configuration is performed in the GUI - there is no need to change any files. When CrackerJack determines that there are zero users in the "users" table, it prompts you to create an administrator.

With regards to Flask and defining where the database file will be located, amongst other settings (like the SECRET_KEY), copy `./files/flask/config.py` to `./data/instance/config.py` and edit accordingly.

# System Service

Create the following directory which will hold our service configuration file:

```
mkdir ./data/config/service
```

## Service Variables

For all the following steps, replace these strings with its representative variables:

Variable | Replace With | Example
--- | --- | ---
{{ webserver.user }} | User running the web server | www-data
{{ webserver.group }} | Group the user running the web server belongs to | www-data
{{ crackerjack.destination }} | Location you cloned CrackerJack to | /opt/crackerjack
{{ service.bind_address }} | Local address to bind application | 127.0.0.1
{{ service.bind_port }} | Port to bind application | 8888

### systemd

#### Configuration File

Copy:

```
./setup/ansible/roles/service/templates/ubuntu/systemd.j2
```

to

```
./data/config/service/crackerjack.service
```

Replace all the variables in that file following the [variables section](#service-variables)

#### Install and Enable Service

Now that you have your service file, run the following:

```
# Create a soft link between your configuration and the systemd folder.
sudo ln -s /absolute/path/to/data/config/service/crackerjack.service /etc/systemd/system/crackerjack.service

# Enable service
sudo systemctl enable crackerjack.service

# Start service
sudo systemctl start crackerjack.service

# Check service
sudo systemctl status crackerjack.service
```

### init.d

#### Configuration File

Copy:

```
./setup/ansible/roles/service/templates/ubuntu/initd.j2
```

to

```
./data/config/service/crackerjack.service
```

Replace all the variables in that file following the [variables section](#service-variables)

#### Install and Enable Service

Now that you have your service file, run the following:

```
# Copy your config file to the init.d directory, then make it executable.
sudo copy /absolute/path/to/data/config/service/crackerjack.service /etc/init.d/crackerjack
sudo chmod +x /etc/init.d/crackerjack

# Enable service
sudo update-rc.d crackerjack defaults

# Start service
sudo service crackerjack start

# Check service
sudo service crackerjack status
```

# Web Server

Create the following directory which will hold our service configuration file:

```
mkdir ./data/config/http
```

## Virtual Host Variables

For all the following steps, replace these strings with its representative variables:

Variable | Replace With | Example
--- | --- | ---
{{ crackerjack.domain }} | Domain CrackerJack will be accessible from | crackerjack.lan
{{ crackerjack.destination }} | Location you cloned CrackerJack to | /opt/crackerjack
{{ service.bind_address }} | Local address the application is running on | 127.0.0.1
{{ service.bind_port }} | Port of local application | 8888

## SSL Certificates

If you have your own SSL certificates, put them in the following location:

```
./data/config/http/ssl.crt
./data/config/http/ssl.pem
```

You can also change the `SSLCertificateFile` and `SSLCertificateKeyFile` locations in the vhost.conf file.

If you want to generate self-signed certificates, use the following command (change the paths where appropriate):

```
openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -keyout /absolute/path/to/data/config/http/ssl.pem -out /absolute/path/to/data/config/http/ssl.crt
```

## Apache

### Install

Ubuntu
```
sudo apt install apache2
sudo a2enmod proxy proxy_http rewrite ssl
```

### Configuration File

Copy 

```
./setup/ansible/roles/webserver/templates/ubuntu/apache/vhost.conf.j2
```

To

```
./data/config/http/vhost.conf
```

Replace all the variables in that file following the [variables section](#virtual-host-variables)

### Enable Site

```
# Link file to sites-available
sudo ln -s /absolut/path/to/data/config/http/vhost.conf /etc/apache2/sites-available/crackerjack.conf

# Enable site
sudo a2ensite crackerjack.conf
```

## nginx

### Install

```
sudo apt install nginx
```

### Configuration File

Copy 

```
./setup/ansible/roles/webserver/templates/ubuntu/nginx/vhost.conf.j2
```

To

```
./data/config/http/vhost.conf
```

### Enable Site

```
# Link file to sites-enabled
sudo ln -s /absolute/path/to/data/config/http/vhost.conf /etc/nginx/sites-enabled/crackerjack

# Restart nginx
```

# .hashcat directory

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
