import os
import re
import time
from pathlib import Path
from flask import current_app
import shutil


class SessionFileSystem:
    def __init__(self, filesystem):
        self.filesystem = filesystem

    def get_data_path(self):
        path = Path(current_app.root_path)
        return os.path.join(str(path.parent), 'data')

    def get_data_sessions_path(self):
        return os.path.join(self.get_data_path(), 'sessions')

    def get_user_data_path(self, user_id, session_id):
        path = os.path.join(self.get_data_sessions_path(), str(user_id))
        if session_id > 0:
            path = os.path.join(path, str(session_id))

        if not os.path.isdir(path):
            os.makedirs(path)

        return path

    def get_hashfile_path(self, user_id, session_id):
        return os.path.join(self.get_user_data_path(user_id, session_id), 'hashes.txt')

    def get_custom_file_path(self, user_id, session_id, prefix='', random=False, extension='.dict'):
        if len(prefix) == 0:
            random = True

        name = prefix
        if random:
            name = name + str(int(time.time()))
        name = name + extension

        return os.path.join(self.get_user_data_path(user_id, session_id), name)

    def custom_file_exists(self, file_path):
        return os.path.isfile(file_path)

    def hashfile_exists(self, user_id, session_id):
        path = self.get_hashfile_path(user_id, session_id)
        return os.path.isfile(path)

    def get_potfile_path(self, user_id, session_id):
        return os.path.join(self.get_user_data_path(user_id, session_id), 'hashes.potfile')

    def get_screenfile_path(self, user_id, session_id, name=None):
        if name is None:
            name = 'screen.log'
        return os.path.join(self.get_user_data_path(user_id, session_id), name)

    def get_crackedfile_path(self, user_id, session_id):
        return os.path.join(self.get_user_data_path(user_id, session_id), 'hashes.cracked')

    def count_non_empty_lines_in_file(self, file):
        if not os.path.isfile(file):
            return 0

        size = os.path.getsize(file)
        max_size = 100 * 1024 * 1024 # 100 MB.
        if size > max_size:
            # File is too large, don't count it.
            return -1

        try:
            count = 0
            with open(file, 'r') as f:
                for line in f:
                    if line.strip():
                        count += 1
        except UnicodeDecodeError:
            count = 0

        return count

    def backup_screen_log_file(self, user_id, session_id):
        path = self.get_screenfile_path(user_id, session_id)
        if not os.path.isfile(path):
            return True

        new_path = path + '.' + str(int(time.time()))
        os.rename(path, new_path)
        return True

    def __remove_escape_characters(self, data):
        # https://stackoverflow.com/questions/14693701/how-can-i-remove-the-ansi-escape-sequences-from-a-string-in-python
        ansi_escape_8bit = re.compile(br'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
        return ansi_escape_8bit.sub(b'', data)

    def __fix_line_termination(self, data):
        return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")

    def tail_file(self, file, length):
        if not os.path.isfile(file):
            return b''

        # If we try to read more than the actual size of the file, it will throw an error.
        filesize = os.path.getsize(file)
        bytes_to_read = filesize if filesize < length else length

        # Read the last 4KB from the screen log file.
        with open(file, 'rb') as file:
            file.seek(bytes_to_read * -1, os.SEEK_END)
            stream = file.read()

        # Replace \r\n with \n, and any rebel \r to \n. We only like \n in here!
        # Clean the file from escape characters.
        stream = self.__remove_escape_characters(stream)
        stream = self.__fix_line_termination(stream)

        return stream

    def save_hashes(self, user_id, session_id, hashes):
        save_as = self.get_hashfile_path(user_id, session_id)
        return self.write_to_file(save_as, hashes)

    def write_to_file(self, file, data):
        with open(file, 'w') as f:
            f.write(data)

        return True

    def find_latest_screenlog(self, user_id, session_id):
        # Sometimes when a backup of screen.log is made, a new "screen.log" doesn't appear, making it look like it's a brand new session.
        # This function will try and find any historical screen.log.TIMESTAMP files in the event of this edge case.
        filepath = self.get_screenfile_path(user_id, session_id)
        if os.path.isfile(filepath):
            return filepath

        filename = os.path.basename(filepath)
        path = os.path.dirname(filepath)
        files = self.filesystem.get_files(path)

        screen_files = []
        len_to_look_for = len(filename) + 1
        for name, data in files.items():
            if name[:len_to_look_for] == (filename + '.'):
                screen_files.append(name)

        if len(screen_files) == 0:
            # Return the original path if no historic files exist.
            return filepath

        screen_files.sort(reverse=True)

        return os.path.join(path, screen_files[0])

    def delete_path(self, path):
        return shutil.rmtree(path)

    def read_file(self, file):
        if not os.path.isfile(file):
            return ''

        with open(file, 'r') as f:
            contents = f.read()

        return contents
