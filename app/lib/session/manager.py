import re, random, string, os, pprint
from app.lib.models.session import SessionModel
from app.lib.models.hashcat import HashcatModel, UsedWordlistModel
from app import db
from pathlib import Path
from sqlalchemy import and_, desc
from flask import current_app


class SessionManager:
    def __init__(self, hashcat, screens):
        self.hashcat = hashcat
        self.screens = screens

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

    def get_screenfile_path(self, user_id):
        return os.path.join(self.get_user_data_path(user_id), 'screen.log')

    def get_crackedfile_path(self, user_id):
        return os.path.join(self.get_user_data_path(user_id), 'hashes.cracked')

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
                'screen_name': session.screen_name,
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
            # When the wordlist is updated, add the previous wordlist to the "used_wordlists" table.
            if record.wordlist != value:
                used = UsedWordlistModel(
                    session_id=session_id,
                    wordlist=record.wordlist
                )
                db.session.add(used)

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

    def action_start(self, session_id):
        # First get the session.
        session = self.get(session_id=session_id)[0]

        # Make sure the screen is running.
        screen = self.screens.get(session['screen_name'], log_file=self.get_screenfile_path(session['user_id']))

        command = self.hashcat.build_command_line(
            session['name'],
            session['hashcat']['mode'],
            session['hashcat']['hashtype'],
            self.get_hashfile_path(session['user_id']),
            session['hashcat']['wordlist_path'],
            self.get_crackedfile_path(session['user_id']),
            self.get_potfile_path(session['user_id']),
            False
        )

        screen.execute(command)

        return True

    def get_used_wordlists(self, session_id):
        return UsedWordlistModel.query.filter(UsedWordlistModel.session_id == session_id).all()

    def __remove_escape_characters(self, data):
        # https://stackoverflow.com/questions/14693701/how-can-i-remove-the-ansi-escape-sequences-from-a-string-in-python
        ansi_escape_8bit = re.compile(br'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
        return ansi_escape_8bit.sub(b'', data)

    def __fix_line_termination(self, data):
        return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")

    def get_hashcat_status(self, session_id):
        # Load the session.
        session = self.get(session_id=session_id)[0]

        # Read the last 5KB from the screen log file.
        stream = ''
        with open(self.get_screenfile_path(session['user_id']), 'rb') as file:
            file.seek(-1024 * 5, os.SEEK_END)
            stream = file.read()

        # Replace \r\n with \n, and any rebel \r to \n. We only like \n in here!
        # Clean the file from escape characters.
        stream = self.__remove_escape_characters(stream)
        stream = self.__fix_line_termination(stream)

        # Pass to hashcat class to parse and return a dict with all the data.
        data = self.hashcat.parse_stream(stream)

        return data


