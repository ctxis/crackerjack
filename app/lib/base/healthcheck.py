import os
import sys
from packaging import version


class HealthCheck:
    def run(self, provider):
        errors = []

        settings = provider.settings()
        screens = provider.screens()
        sessions = provider.sessions()
        shell = provider.shell()

        self.check_python_version("3.6.0", errors)
        self.check_settings(settings, errors)
        self.check_screens(screens, errors)
        self.check_datapath(sessions, errors)
        self.check_screen_software(shell, errors)

        return errors

    def check_python_version(self, minimum_version, errors):
        current_version = str(sys.version_info.major) + '.' + str(sys.version_info.minor) + '.' +  str(sys.version_info.micro)

        if version.parse(current_version) >= version.parse(minimum_version):
            return True

        error_message = 'You are running Python v%d.%d.%d while the minimum supported version is v%s. Please upgrade Python and try again.' % \
                        (sys.version_info.major, sys.version_info.minor, sys.version_info.micro, minimum_version)
        errors.append(error_message)
        return False

    def check_settings(self, settings, errors):
        hashcat_binary = settings.get('hashcat_binary', '')
        wordlists_path = settings.get('wordlists_path', '')

        if len(hashcat_binary) == 0 or not os.path.isfile(hashcat_binary):
            errors.append('Hashcat executable does not exist')
        elif not os.access(hashcat_binary, os.X_OK):
            errors.append('Hashcat file is not executable')

        if len(wordlists_path) == 0 or not os.path.isdir(wordlists_path):
            errors.append('Wordlist directory does not exist')
        elif not os.access(wordlists_path, os.R_OK):
            errors.append('Wordlist directory is not readable')

    def check_screens(self, screens, errors):
        screenrc_path = screens.get_screenrc_path()

        if not os.path.isfile(screenrc_path):
            errors.append(screenrc_path + ' does not exist')
        elif not os.access(screenrc_path, os.R_OK):
            errors.append(screenrc_path + ' is not readable')

    def check_datapath(self, sessions, errors):
        datapath = sessions.session_filesystem.get_data_path()

        if not os.path.isdir(datapath):
            errors.append(datapath + ' does not exist')
        elif not os.access(datapath, os.W_OK):
            errors.append(datapath + ' is not writable')

    def check_screen_software(self, shell, errors):
        screen_binary = shell.execute(['which', 'screen'], user_id=0, log_to_db=False)
        if len(screen_binary) == 0:
            errors.append('screen binary does not exist')
            # No need to keep checking.
            return False

        output = shell.execute(['screen', '--help'], user_id=0, log_to_db=False)
        if "-Logfile" not in output:
            errors.append(
                'The *screen* application seems to be out of date. In order for CrackerJack to work it will need to be v4.06 or higher, as those versions introduced the -Logfile parameter which is required.')
