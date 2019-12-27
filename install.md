# Install

## Requirements

* python >= 3.6
    * In python 3.6 onwards dictionaries hold items in the same order you add them. Sounds to me this should have been the deal since version 1.
* screen >= 4.06.00
    * This version of screen onwards has the -Logfile parameter where you can set the output path of the logfile.
* hashcat
    * Any version will do, all supported hashes are dynamically extracted from the --help option.

## Setup Environment

### Virtual Environment
```
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
flask db init
flask db migrate
flask db upgrade
deactivate
```

### Folder permissions
Within the root folder, run:
```
sudo chown -R www-data:www-data ./instance ./data
``` 

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