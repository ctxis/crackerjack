import subprocess
import datetime
import shlex

from sqlalchemy import and_, desc

from app.lib.models.system import ShellLogModel
from app.lib.models.user import UserModel
from app import db


class ShellManager:
    def __init__(self, user_id=0):
        self.user_id = user_id

    def execute(self, command, user_id=None):
        user_id = self.user_id if user_id is None else user_id
        log = self.__log_start(' '.join(command), user_id)

        output = subprocess.run(command, stdout=subprocess.PIPE).stdout.decode().strip()

        log = self.__log_finish(log, output)

        return output

    def build_command_from_dict(self, command):
        sanitised = []
        for key, value in command.items():
            item = shlex.quote(key)
            if isinstance(value, str) and len(value) > 0:
                item = item + ' ' + shlex.quote(value)
            else:
                item = item + ' ' + str(value)

            sanitised.append(item.strip())

        return sanitised

    def __log_start(self, command, user_id):
        record = ShellLogModel(user_id=user_id, command=command, executed_at=datetime.datetime.now())
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

    def get_logs(self, user_id=-1, page=0, per_page=0):
        conditions = and_(1 == 1)
        # 0 is reserved for the system.
        if user_id >= 0:
            conditions = and_(ShellLogModel.user_id == user_id)

        logs = ShellLogModel.query \
            .outerjoin(UserModel, ShellLogModel.user_id == UserModel.id) \
            .add_columns(
                ShellLogModel.id,
                ShellLogModel.user_id,
                ShellLogModel.command,
                ShellLogModel.output,
                ShellLogModel.executed_at,
                ShellLogModel.finished_at,
                UserModel.username
            ) \
            .filter(conditions) \
            .order_by(desc(ShellLogModel.id))

        if page == 0 and per_page == 0:
            logs = logs.all()
        else:
            logs = logs.paginate(page, per_page, False)

        return logs
