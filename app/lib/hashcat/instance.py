import os
from app.lib.models.hashcat import HashcatModel


class HashcatInstance:
    def __init__(self, session, filesystem, manager, wordlists):
        self.session = session
        self.filesystem = filesystem
        self.hashcat = manager
        self.wordlists = wordlists
        self.settings = HashcatModel.query.filter(HashcatModel.session_id == session.id).first()

        self._screen_log_file_path = None
        self._tail_screen = None
        self._state = None
        self._hashcat_raw_data = None
        self._data = None
        self._cracked_passwords = None
        self._all_passwords = None
        self._progress = None
        self._time_remaining = None
        self._estimated_completion_time = None

    @property
    def state(self):
        if self._state is None:
            self._state = self.data['process_state']
        return self._state

    @property
    def state_description(self):
        return self.__get_state_description(self.state)

    @property
    def cracked_passwords(self):
        if self._cracked_passwords is None:
            self._cracked_passwords = self.data['cracked_passwords']
        return self._cracked_passwords

    @property
    def all_passwords(self):
        if self._all_passwords is None:
            self._all_passwords = self.data['all_passwords']
        return self._all_passwords

    @property
    def progress(self):
        if self._progress is None:
            self._progress = self.data['progress']
        return self._progress

    @property
    def time_remaining(self):
        if self._time_remaining is None:
            self._time_remaining = self.data['time_remaining']
        return self._time_remaining

    @property
    def estimated_completion_time(self):
        if self._estimated_completion_time is None:
            self._estimated_completion_time = self.data['estimated_completion_time']
        return self._estimated_completion_time

    @property
    def screen_log_file_path(self):
        if self._screen_log_file_path is None:
            self._screen_log_file_path = self.filesystem.find_latest_screenlog(self.session.user_id, self.session.id)
        return self._screen_log_file_path

    @property
    def tail_screen(self):
        if self._tail_screen is None:
            self._tail_screen = self.__load_tail_screen(4, 5, 1)
        return self._tail_screen

    @property
    def hashcat_data_raw(self):
        if self._hashcat_raw_data is None:
            self._hashcat_raw_data = self.__get_hashcat_status()
        return self._hashcat_raw_data

    @property
    def data(self):
        if self._data is None:
            self._data = self.hashcat.process_hashcat_raw_data(self.hashcat_data_raw, self.session.screen_name, self.tail_screen)
        return self._data

    @property
    def data_raw(self):
        return self.hashcat_data_raw

    @property
    def increment_min(self):
        return self.settings.increment_min if self.settings else 0

    @property
    def increment_max(self):
        return self.settings.increment_max if self.settings else 0

    @property
    def increment_enabled(self):
        return self.increment_min > 0 and self.increment_max > 0

    @property
    def mode(self):
        return self.settings.mode if self.settings else ''

    @property
    def hashtype(self):
        return self.settings.hashtype if self.settings else ''

    @property
    def wordlist_type(self):
        return self.settings.wordlist_type if self.settings else 0

    @property
    def wordlist_path(self):
        return self.settings.wordlist if self.settings else ''

    @property
    def wordlist(self):
        return self.wordlists.get_name_from_path(self.wordlist_path) if self.settings else ''

    @property
    def rule_path(self):
        return self.settings.rule if self.settings else ''

    @property
    def rule(self):
        return os.path.basename(self.settings.rule) if self.settings else ''

    @property
    def mask(self):
        return self.settings.mask if self.settings else ''

    @property
    def optimised_kernel(self):
        return self.settings.optimised_kernel if self.settings else 0

    @property
    def configured(self):
        return True if self.settings else False

    def __get_hashcat_status(self):
        return self.hashcat.parse_stream(self.tail_screen)

    def __load_tail_screen(self, kb_to_read, kb_max, step=1):
        data = ''
        try:
            data = self.filesystem.tail_file(self.screen_log_file_path, kb_to_read * 1024).decode()
        except UnicodeDecodeError:
            # This means that we probably got half a unicode sequence. Increase the buffer and try again.
            next_size = kb_to_read + step
            if next_size <= kb_max:
                data = self.__load_tail_screen(next_size, kb_max, step)

        return data

    def __get_state_description(self, state):
        description = 'Unknown'

        if state == 0:
            description = 'Not Started'
        elif state == 1:
            description = 'Running'
        elif state == 2:
            description = 'Stopped'
        elif state == 3:
            description = 'Finished'
        elif state == 4:
            description = 'Paused'
        elif state == 5:
            description = 'Cracked'
        elif state == 98:
            description = 'Error'
        elif state == 99:
            description = 'Unknown'

        return description
