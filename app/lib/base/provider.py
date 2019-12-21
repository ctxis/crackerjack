from app.lib.base.settings import SettingsManager
from app.lib.session.manager import SessionManager
from app.lib.base.healthcheck import HealthCheck
from app.lib.screen.manager import ScreenManager
from app.lib.hashcat.manager import HashcatManager
from app.lib.base.shell import ShellManager
from app.lib.base.wordlists import WordlistManager
from app.lib.base.system import SystemManager
from app.lib.base.filesystem import FileSystemManager
from app.lib.base.rules import RulesManager
from app.lib.base.ldap import LDAPManager
from app.lib.base.users import UserManager
from app.lib.base.user_settings import UserSettingsManager


class Provider:
    def settings(self):
        settings = SettingsManager()
        return settings

    def sessions(self):
        session = SessionManager(
            self.hashcat(),
            self.screens()
        )
        return session

    def healthcheck(self):
        return HealthCheck()

    def screens(self):
        return ScreenManager(self.shell())

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
        return WordlistManager(self.filesystem(), settings.get('wordlists_path', ''))

    def system(self):
        return SystemManager(
            self.shell(),
            self.settings()
        )

    def filesystem(self):
        return FileSystemManager()

    def rules(self):
        settings = self.settings()
        return RulesManager(self.filesystem(), settings.get('hashcat_rules_path', ''))

    def ldap(self):
        settings = self.settings()
        manager = LDAPManager()

        manager.enabled = settings.get('ldap_enabled', 0)
        manager.host = settings.get('ldap_host', '')
        manager.base_dn = settings.get('ldap_base_dn', '')
        manager.domain = settings.get('ldap_domain', '')
        manager.bind_user = settings.get('ldap_bind_user', '')
        manager.bind_pass = settings.get('ldap_bind_pass', '')
        manager.mapping_username = settings.get('ldap_mapping_username', '')
        manager.mapping_firstname = settings.get('ldap_mapping_firstname', '')
        manager.mapping_lastname = settings.get('ldap_mapping_lastname', '')
        manager.mapping_email = settings.get('ldap_mapping_email', '')

        return manager

    def users(self):
        return UserManager()

    def user_settings(self):
        return UserSettingsManager()
