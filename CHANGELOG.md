# Changelog

## v1.1.0

* `[Update]` Updated hashcatid with newly supported hashes in v6.2.1.
* `[Fix]` Fix issue with LDAP password change for users that have never logged in before.
* `[Update]` Update ansible scripts to support Ubuntu 20.
* `[Update]` Refactor settings page UI.
* `[Fix]` Updated systemd settings to prevent screen child processed to be killed when service is restarted/stopped.
* `[New]` Added semantic versioning.
* `[Fix]` Prevent Flask v2 from being installed.
* `[Fix]` Stop logging shell commands that are not very useful.
* `[Fix]` Implement support for parsing hashes from older versions of hashcat (See issue #9).
* `[Fix]` Fix CSRF issue due to lack of the referer header (See issue #5).
* `[Fix]` Fix password complexity check (See issue #8).

## v1.0.1

* `[Update]` Implement hashcatid from scratch.
* `[New]` Implement modules and incorporate office2hashcat into the UI.
* `[Fix]` Fix raw errors from not being displayed in the session page.
* `[New]` Implement support for the --username parameter.
* `[New]` Implement session page to browse through cracked passwords when those have been uploaded along with their usernames.