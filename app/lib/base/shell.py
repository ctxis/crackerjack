import subprocess
import datetime
from app.lib.models.system import ShellLogModel
from app import db


class ShellManager:
    def __init__(self, user_id=0):
        self.user_id = user_id

    def execute(self, command):
        log = self.__log_start(' '.join(command))

        output = subprocess.run(command, stdout=subprocess.PIPE).stdout.decode().strip()

        log = self.__log_finish(log, output)

        return output

    def __log_start(self, command):
        record = ShellLogModel(user_id=self.user_id, command=command)
        # Add
        db.session.add(record)
        # Save
        db.session.commit()
        # Commit
        db.session.refresh(record)

        return record

    def __log_finish(self, record, output):
        record.output = output
        record.output = output
        record.finished_at = datetime.datetime.now()
        db.session.commit()
        db.session.refresh(record)

        return record
