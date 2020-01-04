import subprocess
import datetime
from app.lib.models.system import ShellLogModel
from app import db


class ShellManager:
    def __init__(self, user_id=0):
        self.user_id = user_id

    def execute(self, command):
        log = ShellLogModel()
        log.user_id = self.user_id
        log.command = ' '.join(command)
        # Add
        db.session.add(log)
        # Save
        db.session.commit()
        # Commit
        db.session.refresh(log)

        output = subprocess.run(command, stdout=subprocess.PIPE).stdout.decode().strip()

        log.output = output
        log.finished_at = datetime.datetime.now()
        db.session.commit()
        db.session.refresh(log)

        return output
