import os
import getpass
import datetime


class SystemManager:
    def __init__(self, shell, settings):
        self.shell = shell
        self.settings = settings

    def run_updates(self):
        self.update_hashcat_version()
        self.update_git_hash_version()

    def update_hashcat_version(self):
        hashcat_binary = self.settings.get('hashcat_binary', '')
        if len(hashcat_binary) == 0:
            return False
        elif not os.path.isfile(hashcat_binary):
            return False
        elif not os.access(hashcat_binary, os.X_OK):
            return False

        version = self.shell.execute([hashcat_binary, '--version'], user_id=0)
        self.settings.save('hashcat_version', version)
        return True

    def update_git_hash_version(self):
        git_binary = self.shell.execute(['which', 'git'], user_id=0)
        if len(git_binary) == 0:
            return False

        # Save latest commit short hash.
        version = self.shell.execute(['git', 'rev-parse', '--short', 'HEAD'], user_id=0)
        self.settings.save('git_hash_version', version)

        # Save commit count on the master branch (like a version tracker).
        try:
            count = int(self.shell.execute(['git', 'rev-list', '--count', 'master'], user_id=0))
        except ValueError:
            count = 0
        self.settings.save('git_commit_count', count)

        # Save last commit date.
        try:
            last_commit_timestamp = int(self.shell.execute(['git', 'log', '-1', '--format=%at'], user_id=0))
        except ValueError:
            last_commit_timestamp = 0

        last_commit_date = ''
        if last_commit_timestamp > 0:
            last_commit_date = datetime.datetime.fromtimestamp(last_commit_timestamp).strftime('%Y-%m-%d %H:%M')
        self.settings.save('last_commit_date', last_commit_date)

        return True

    def get_system_user(self):
        return getpass.getuser()

    def get_system_user_home_directory(self, user=""):
        if len(user) == 0:
            user = self.get_system_user()

        return self.shell.execute(['/bin/bash', '-c', 'eval echo ~' + user], user_id=0)
