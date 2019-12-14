from app.lib.base.settings import SettingsManager
from app.lib.session.manager import SessionManager
from app.lib.base.healthcheck import HealthCheck
from app.lib.screen.manager import ScreenManager
from app.lib.hashcat.manager import HashcatManager
from app.lib.base.shell import ShellManager
from app.lib.base.wordlists import WordlistManager


class Provider:
    def settings(self):
        settings = SettingsManager()
        return settings

    def sessions(self):
        session = SessionManager()
        return session

    def healthcheck(self):
        return HealthCheck()

    def screens(self):
        return ScreenManager()

    def hashcat(self):
        settings = self.settings()
        return HashcatManager(
            self.shell(),
            settings.get('hashcat_binary', '')
        )

    def shell(self):
        return ShellManager()

    def wordlists(self):
        settings = self.settings()
        return WordlistManager(settings.get('wordlists_path'))
