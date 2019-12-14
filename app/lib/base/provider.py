from app.lib.base.settings import SettingsManager
from app.lib.session.manager import SessionManager
from app.lib.base.healthcheck import HealthCheck
from app.lib.screen.manager import ScreenManager


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