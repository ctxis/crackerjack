from app.lib.base.settings import SettingsManager
from app.lib.session.manager import SessionManager


class Provider:
    def settings(self):
        settings = SettingsManager()

        return settings

    def sessions(self):
        session = SessionManager()

        return session
