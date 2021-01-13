import os
from app.lib.models.user import UserModel
from app.lib.models.hashcat import HashcatHistoryModel
from sqlalchemy import desc


class SessionInstance:
    def __init__(self, session, hashcat, filesystem):
        self.session = session
        self.hashcat = hashcat
        self.filesystem = filesystem
        self.user = UserModel.query.filter(UserModel.id == session.user_id).first()

        self._hashes_in_file = None
        self._hashfile = None

    @property
    def id(self):
        return self.session.id

    @property
    def description(self):
        return self.session.description

    @property
    def name(self):
        return self.session.name

    @property
    def username(self):
        return self.user.username

    @property
    def terminate_at(self):
        return self.session.terminate_at

    @property
    def user_id(self):
        return self.session.user_id

    @property
    def screen_name(self):
        return self.session.screen_name

    @property
    def active(self):
        return self.session.active

    @property
    def notifications_enabled(self):
        return self.session.notifications_enabled

    @property
    def created_at(self):
        return self.session.created_at

    @property
    def friendly_name(self):
        return self.session.description if len(self.session.description) > 0 else self.session.name

    @property
    def hashfile(self):
        if self._hashfile is None:
            self._hashfile = self.filesystem.get_hashfile_path(self.session.user_id, self.session.id)
        return self._hashfile

    @property
    def hashes_in_file(self):
        if self._hashes_in_file is None:
            self._hashes_in_file = self.filesystem.count_non_empty_lines_in_file(self.hashfile)
        return self._hashes_in_file

    @property
    def hashfile_exists(self):
        return os.path.isfile(self.hashfile)

    @property
    def validation(self):
        return self.__validate()

    def __validate(self):
        errors = []

        # First check if hashes have been uploaded.
        if self.hashes_in_file == 0:
            errors.append('No hashes have been uploaded')

        # Now we check the hashtype.
        if self.hashcat.hashtype == '':
            errors.append('No hash type has been selected')

        # Check attack mode settings.
        if self.hashcat.mode == 0:
            # Do checks for wordlist attacks.
            if self.hashcat.wordlist == '':
                errors.append('No wordlist has been selected')
        else:
            # Do checks for bruteforce attacks.
            if self.hashcat.mask == '':
                errors.append('No mask has been set')

        # Check termination date
        if self.terminate_at is None:
            errors.append('No termination date has been set')

        return errors

    @property
    def hashcat_history(self):
        return HashcatHistoryModel.query.filter(
            HashcatHistoryModel.session_id == self.id
        ).order_by(desc(HashcatHistoryModel.id)).all()
