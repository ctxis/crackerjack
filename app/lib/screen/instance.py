import time, shlex


class ScreenInstance:
    def __init__(self, shell):
        self.cmd_sleep = 2
        self.shell = shell

        self._id = 0
        self._name = ''
        self._datetime = ''
        self._state = ''

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def datetime(self):
        return self._datetime

    @datetime.setter
    def datetime(self, value):
        self._datetime = value

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    def execute(self, command):
        # Read more here: https://www.gnu.org/software/screen/manual/screen.html

        # Cannot pass the "command" variable as a list to shell.execute() because screen expects it to be passed as
        # a string instead. Therefore, although the command argument is a dict, we manually escape all of it.
        sanitised = []
        for key, value in command.items():
            item = shlex.quote(key)
            if isinstance(value, str) and len(value) > 0:
                item = item + ' ' + shlex.quote(value)
            else:
                item = item + ' ' + str(value)

            sanitised.append(item)

        # Paste command into the input buffer.
        cmd = [
            'screen',
            '-x',
            self.name,
            '-X',
            'stuff',
            ' '.join(sanitised)
        ]

        output = self.shell.execute(cmd)

        # Wait a couple of seconds.
        time.sleep(self.cmd_sleep)

        # Press ENTER.
        output = self.shell.execute(
            [
                'screen',
                '-x',
                self.name,
                '-X',
                'stuff',
                '\\015'
            ]
        )

        return True
