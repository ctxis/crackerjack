from flask import current_app
from pathlib import Path
import os
from app.lib.screen.instance import ScreenInstance


class ScreenManager:
    def __init__(self, shell):
        self.shell = shell

    def get_screenrc_path(self):
        path = Path(current_app.root_path)
        return os.path.join(str(path.parent), 'files', 'screen', 'screen.rc')

    def get(self, name, log_file="", create=True):
        screen = self.__find(name)
        if screen:
            return screen

        return self.__create(name, log_file)

    def __create(self, name, log_file):
        command = [
            'screen',
            '-L',
            '-Logfile',
            log_file,
            '-dmS',
            name,
            '-c',
            self.get_screenrc_path()
        ]

        output = self.shell.execute(command, user_id=0)
        return self.__find(name)

    def __find(self, name):
        found_screen = False
        screens = self.__load_screens()

        for screen in screens:
            if screen.name == name:
                found_screen = screen
                break

        return found_screen

    def __load_screens(self):
        output = self.shell.execute(['screen', '-ls'], user_id=0)
        output = self.__split_and_clean(output)

        screens = []
        for line in output:
            screen = self.__load_screen(line)
            if screen is not False:
                screens.append(screen)

        return screens

    def __split_and_clean(self, input, split_by="\n"):
        output = input.split(split_by)
        output = map(str.strip, output)
        output = list(filter(None, output))
        return output

    def __load_screen(self, line):
        data = line.split("\t")
        if len(data) < 2:
            return False

        id, name = data[0].split('.')

        screen = ScreenInstance(self.shell)
        screen.id = id
        screen.name = name

        return screen
