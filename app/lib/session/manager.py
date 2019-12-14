import re, random, string, os
from app.lib.models.session import SessionModel
from app import db
from pathlib import Path
from sqlalchemy import and_, desc
from flask import current_app


class SessionManager:
    def sanitise_name(self, name):
        return re.sub(r'\W+', '', name)

    def generate_name(self, prefix=''):
        return prefix + ''.join(random.choice(string.ascii_letters + string.digits) for i in range(12))

    def __generate_screen_name(self, user_id, name):
        return str(user_id) + '_' + name;

    def exists(self, user_id, name, active=True):
        return self.__get(user_id, name, active) is not None

    def __get(self, user_id, name, active):
        return SessionModel.query.filter(
            and_(
                SessionModel.user_id == user_id,
                SessionModel.name == name,
                SessionModel.active == active
            )
        ).first()

    def create(self, user_id, name):
        session = self.__get(user_id, name, True)
        if session:
            # Return existing session if there is one.
            return session

        session = SessionModel(
            user_id=user_id,
            name=name,
            active=True,
            screen_name=self.__generate_screen_name(user_id, name)
        )
        db.session.add(session)
        db.session.commit()
        # In order to get the created object, we need to refresh it.
        db.session.refresh(session)

        return session

    def get_data_path(self):
        path = Path(current_app.root_path)
        return os.path.join(str(path.parent), 'data')

    def get_user_data_path(self, user_id):
        path = os.path.join(self.get_data_path(), str(user_id))
        if not os.path.isdir(path):
            os.makedirs(path)

        return path

    def get_hashfile_path(self, user_id):
        return os.path.join(self.get_user_data_path(user_id), 'hashes.txt')

    def can_access(self, user, session_id):
        if user.admin:
            return True

        session = SessionModel.query.filter(
            and_(
                SessionModel.user_id == user.id,
                SessionModel.id == session_id
            )
        ).first()

        return True if session else False

    def get(self, user_id=0, session_id=0):
        conditions = and_(1 == 1)
        if user_id > 0 and session_id > 0:
            conditions = and_(SessionModel.user_id == user_id, SessionModel.id == session_id)
        elif user_id > 0:
            conditions = and_(SessionModel.user_id == user_id)
        elif session_id > 0:
            conditions = and_(SessionModel.id == session_id)

        sessions = SessionModel.query.filter(conditions).order_by(desc(SessionModel.id)).all()

        data = []
        for session in sessions:
            item = {
                'id': session.id,
                'name': session.name,
                'user_id': session.user_id,
                'created_at': session.created_at,
                'active': session.active
            }

            data.append(item)

        return data
