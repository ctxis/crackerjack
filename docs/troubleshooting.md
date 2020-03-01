# CrackerJack / Troubleshooting

## The GUI doesn't work at all
1. Check that the `crackerjack` service is running using:
    1. `sudo systemctl status crackerjack` or
    2. `ps -aux | grep crackerjack` (you should see 4 workers).
2. Check that apache/nginx are running, and have a look at their log files in `/var/log`
3. Check that the whole `/crackerjack` directory is owned by the `www-data` user (or whichever user is running your web server). 
4. If it's still not working, create a new issue in the repo.

## Cannot start a new session
1. Login to your server via SSH
2. Switch to the www-data user (or whichever user is running your web server)
3. Run `screen -ls`
4. Screen names have the following format: `USERID_USERNAME_RANDOMSEED_SESSIONID`
    1. Which means if your session URL is `/sessions/4/view` and your username is `admin`, the screen name will be: `SOMEID_admin_XXXX_4`
5. Attach to the screen using `screen -r SCREEN_NAME`
6. Click the `start` button via the GUI and check if that screen instance is receiving the command and check its output.
7. Make sure that the user that's running the web server has a `.hashcat` directory in their home directory, for example `/var/www/.hashcat`

## Web Push notifications don't work
1. Check that the crontab has been installed.
    1. Login as the `www-data` (or equivalent) user, and run `crontab -l`.
2. Make sure you are not using self-signed certificates, use LetsEncrypt.
3. Check the `syslog`.

## Sessions aren't terminated after the termination date.
1. Check that the crontab has been installed.
    1. Login as the `www-data` (or equivalent) user, and run `crontab -l`.
2. Check the `syslog`.