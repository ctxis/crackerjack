# Changelog

## v1.1.3

* `[Update]` Add 'SIMPLE' as an LDAP Authentication type.
* `[Update]` Show 'Restore' button when a session errors out.
* `[Fix]` When using a custom wordlist, allow to change the ruleset without having to re-upload the file.

## v1.1.2

* `[New]` Added "Test Connection" feature to LDAP settings.

## v1.1.1

* `[Update]` If hashcat >= v6.2.3 is installed, use the built-in `--id --mach [hash]` functionality to identify a hash.

## v1.1.0

* `[New]` Added semantic versioning.
* `[Update]` Updated hashcatid with newly supported hashes in v6.2.1.
* `[Update]` Update ansible scripts to support Ubuntu 20.
* `[Update]` Refactor settings page UI.
* `[Fix]` Updated systemd settings to prevent screen child processed to be killed when service is restarted/stopped.
* `[Fix]` Fix issue with LDAP password change for users that have never logged in before.
* `[Fix]` Prevent Flask v2 from being installed.
* `[Fix]` Stop logging shell commands that are not very useful.
* `[Fix]` Implement support for parsing hashes from older versions of hashcat (See issue #9).
* `[Fix]` Fix CSRF issue due to lack of the referer header (See issue #5).
* `[Fix]` Fix password complexity check (See issue #8).
* `[Fix]` Fix hash/password file download when unable to read screen log (See issue #10).

## v1.0.1

* `[New]` Implement modules and incorporate office2hashcat into the UI.
* `[New]` Implement support for the --username parameter.
* `[New]` Implement session page to browse through cracked passwords when those have been uploaded along with their usernames.
* `[Update]` Implement hashcatid from scratch.
* `[Fix]` Fix raw errors from not being displayed in the session page.
