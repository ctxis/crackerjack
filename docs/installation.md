# CrackerJack Installation

* [Requirements](#requirements)
* [Installation](#installation)
  * [Ansible](#ansible)
  * [Manual](manual_installation.md)
* [Third-Party Software](#third-party-software)
  * [Screen](#screen)
  * [Hashcat](#hashcat)


## Requirements

* python >= 3.6
    * In python 3.6 onwards dictionaries hold items in the same order you add them. Sounds to me this should have been the deal since version 1.
* screen >= 4.06.00
    * This version of screen onwards has the -Logfile parameter where you can set the output path of the logfile.
* hashcat
    * Any version will do, all supported hashes are dynamically extracted from the --help option.

## Installation

### Ansible

**WARNING**: The Ansible scripts have been tested only against clean installations of the supported operating systems. Be careful if you run them against an environment with non-standard configuration.

Ansible scripts are provided in the `./setup/ansible` directory.

Copy the `vars.yml.template` file to `vars.yml`, follow the instructions within the file to set the appropriate variables, and run against your host:

```
cd ./setup/ansible
ansible-playbook -K crackerjack.yml -v --user <USER_TO_LOGIN_WITH> --ask-pass -i <IP_OR_HOSTNAME_OF_MACHINE>,
```

### Manual

[For a guide on how to manually install CrackerJack, click here](manual_installation.md).

## Third-Party Software

### Screen

If you are running a linux distribution that doesn't have the latest version in its repos, you can download and compile it from source.

#### Packages
```
sudo apt install libncurses5-dev
```

#### Compile
```
cd ~
wget http://ftp.gnu.org/gnu/screen/screen-4.7.0.tar.gz -O screen.tar.gz
tar -xf screen.tar.gz
cd ./screen-4.7.0
./configure
make
sudo make install
```

#### Check version
```
$ screen --version
Screen version 4.07.00 (GNU) 02-Oct-19
```

### Hashcat

It's recommended to compile hashcat from source - instructions are at https://github.com/hashcat/hashcat/blob/master/BUILD.md

