import re, random, string, os
from app.lib.models.session import SessionModel
from app.lib.models.hashcat import HashcatModel
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

    def get_potfile_path(self, user_id):
        return os.path.join(self.get_user_data_path(user_id), 'hashes.potfile')

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
            hashcat = self.get_hashcat_settings(session.id)

            item = {
                'id': session.id,
                'name': session.name,
                'user_id': session.user_id,
                'created_at': session.created_at,
                'active': session.active,
                'hashcat': {
                    'configured': True if hashcat else False,
                    'mode': '' if not hashcat else hashcat.mode,
                    'hashtype': '' if not hashcat else hashcat.hashtype,
                    'wordlist': '' if not hashcat else os.path.basename(hashcat.wordlist),
                    'wordlist_path': '' if not hashcat else hashcat.wordlist
                }
            }

            data.append(item)

        return data

    def set_hashcat_setting(self, session_id, name, value):
        record = self.get_hashcat_settings(session_id)
        if not record:
            record = self.__create_hashcat_record(session_id)

        if name == 'mode':
            record.mode = value
        elif name == 'hashtype':
            record.hashtype = value
        elif name == 'wordlist':
            record.wordlist = value

        db.session.commit()

    def get_hashcat_settings(self, session_id):
        return HashcatModel.query.filter(HashcatModel.session_id == session_id).first()

    def __create_hashcat_record(self, session_id):
        record = HashcatModel(
            session_id=session_id
        )

        db.session.add(record)
        db.session.commit()
        # In order to get the created object, we need to refresh it.
        db.session.refresh(record)

        return record
