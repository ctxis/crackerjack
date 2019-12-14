import subprocess


class ShellManager:
    def execute(self, command):
        return subprocess.run(command, stdout=subprocess.PIPE).stdout.decode().strip()