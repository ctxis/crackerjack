import os, pprint


class HealthCheck:
    def run(self, provider):
        errors = []

        settings = provider.settings()
        screens = provider.screens()

        self.check_settings(settings, errors)
        self.check_screens(screens, errors)

        return errors

    def check_settings(self, settings, errors):
        allow_logins = settings.get('allow_logins', 0)
        hashcat_binary = settings.get('hashcat_binary', '')
        wordlists_path = settings.get('wordlists_path', '')

        if int(allow_logins) == 0:
            errors.append('Logins are currently disabled.')

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
            errors.append(screenrc_path + ' does not exist.')
        elif not os.access(screenrc_path, os.R_OK):
            errors.append(screenrc_path + ' is not readable')
