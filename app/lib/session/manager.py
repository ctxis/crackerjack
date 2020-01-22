import re
import random
import string
import os
import datetime
import time
from app.lib.models.sessions import SessionModel
from app.lib.models.user import UserModel
from app.lib.models.hashcat import HashcatModel, HashcatHistoryModel
from app.lib.session.filesystem import SessionFileSystem
from app.lib.session.validation import SessionValidation
from app import db
from sqlalchemy import and_, desc
from flask import send_file


class SessionManager:
    def __init__(self, hashcat, screens, wordlists, hashid, filesystem):
        self.hashcat = hashcat
        self.screens = screens
        self.wordlists = wordlists
        self.hashid = hashid
        self.filesystem = filesystem
        self.session_filesystem = SessionFileSystem(filesystem)
        self.session_validation = SessionValidation()
        self.cmd_sleep = 2

    def sanitise_name(self, name):
        return re.sub(r'\W+', '', name)

    def generate_name(self, length=12, prefix=''):
        return prefix + ''.join(random.choice(string.ascii_letters + string.digits) for i in range(length))

    def __generate_screen_name(self, user_id, name):
        return str(user_id) + '_' + name

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

    def __get_by_id(self, session_id):
        return SessionModel.query.filter(SessionModel.id == session_id).first()

    def create(self, user_id, name, description):
        session = self.__get(user_id, name, True)
        if session:
            # Return existing session if there is one.
            return session

        session = SessionModel(
            user_id=user_id,
            name=name,
            description=description,
            active=True,
            screen_name=self.__generate_screen_name(user_id, name)
        )
        db.session.add(session)
        db.session.commit()
        # In order to get the created object, we need to refresh it.
        db.session.refresh(session)

        return session

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
            hashcat_data_raw = self.get_hashcat_status(session.user_id, session.id)
            screen_log_file = self.session_filesystem.find_latest_screenlog(session.user_id, session.id)
            try:
                tail_screen = self.session_filesystem.tail_file(screen_log_file, 4096).decode()
            except UnicodeDecodeError:
                # This means that we probably got half a unicode sequence. Increase the buffer and try again.
                tail_screen = self.session_filesystem.tail_file(screen_log_file, 5120).decode()

            item = {
                'id': session.id,
                'name': session.name,
                'description': session.description,
                'screen_name': session.screen_name,
                'user_id': session.user_id,
                'created_at': session.created_at,
                'terminate_at': session.terminate_at,
                'active': session.active,
                'hashcat': {
                    'configured': True if hashcat else False,
                    'mode': '' if not hashcat else hashcat.mode,
                    'hashtype': '' if not hashcat else hashcat.hashtype,
                    'wordlist': '' if not hashcat else self.wordlists.get_name_from_path(hashcat.wordlist),
                    'wordlist_path': '' if not hashcat else hashcat.wordlist,
                    'rule': '' if not hashcat else os.path.basename(hashcat.rule),
                    'rule_path': '' if not hashcat else hashcat.rule,
                    'mask': '' if not hashcat else hashcat.mask,
                    'increment_min': 0 if not hashcat else hashcat.increment_min,
                    'increment_max': 0 if not hashcat else hashcat.increment_max,
                    'data_raw': hashcat_data_raw,
                    'data': self.hashcat.process_hashcat_raw_data(hashcat_data_raw, session.screen_name, tail_screen),
                    'hashfile': self.session_filesystem.get_hashfile_path(session.user_id, session.id),
                    'hashfile_exists': self.session_filesystem.hashfile_exists(session.user_id, session.id)
                },
                'user': {
                    'record': UserModel.query.filter(UserModel.id == session.user_id).first()
                },
                'tail_screen': tail_screen,
                'hashes_in_file': self.session_filesystem.count_non_empty_lines_in_file(self.session_filesystem.get_hashfile_path(session.user_id, session.id)),
                'guess_hashtype': self.guess_hashtype(session.user_id, session.id),
                'hashcat_history': self.__get_hashcat_history(session_id),
                'validation': {} # This will be set outside to prevent a deadlock as it uses the session itself as input.
            }

            item['validation'] = self.session_validation.validate(item)

            data.append(item)

        return data

    def __get_hashcat_history(self, session_id):
        return HashcatHistoryModel.query.filter(
            HashcatHistoryModel.session_id == session_id
        ).order_by(desc(HashcatHistoryModel.id)).all()

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
        elif name == 'rule':
            record.rule = value
        elif name == 'mask':
            record.mask = value
        elif name == 'increment_min':
            record.increment_min = value
        elif name == 'increment_max':
            record.increment_max = value

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

    def hashcat_action(self, session_id, action):
        # First get the session.
        session = self.get(session_id=session_id)[0]

        # Make sure the screen is running.
        screen = self.screens.get(session['screen_name'], log_file=self.session_filesystem.get_screenfile_path(session['user_id'], session_id))

        if action == 'start':
            if self.__is_past_date(session['terminate_at']):
                return False

            command = self.hashcat.build_command_line(
                session['screen_name'],
                int(session['hashcat']['mode']),
                session['hashcat']['mask'],
                session['hashcat']['hashtype'],
                self.session_filesystem.get_hashfile_path(session['user_id'], session_id),
                session['hashcat']['wordlist_path'],
                session['hashcat']['rule_path'],
                self.session_filesystem.get_crackedfile_path(session['user_id'], session_id),
                self.session_filesystem.get_potfile_path(session['user_id'], session_id),
                int(session['hashcat']['increment_min']),
                int(session['hashcat']['increment_max'])
            )

            # Before we start a new session, rename the previous "screen.log" file
            # so that we can determine errors/state easier.
            self.session_filesystem.backup_screen_log_file(session['user_id'], session_id)

            # Even though we renamed the file, as it is still open the OS handle will now point to the renamed file.
            # We re-set the screen logfile to the original file.
            screen.set_logfile(self.session_filesystem.get_screenfile_path(session['user_id'], session_id))
            screen.execute(command)

            # Every time we start a session, we make a copy of the settings and put them in the hashcat_history table.
            self.__save_hashcat_history(session_id)
        elif action == 'reset':
            # Close the screen.
            screen.quit()

            # Create it again.
            screen = self.screens.get(session['screen_name'], log_file=self.session_filesystem.get_screenfile_path(session['user_id'], session_id))
        elif action == 'resume':
            if self.__is_past_date(session['terminate_at']):
                return False

            # Hashcat only needs 'r' to resume.
            screen.execute({'r': ''})

            # Wait a couple of seconds.
            time.sleep(self.cmd_sleep)

            # Send an "s" command to show current status.
            screen.execute({'s': ''})

            # Wain a second.
            time.sleep(1)
        elif action == 'pause':
            # Hashcat only needs 'p' to pause.
            screen.execute({'p': ''})

            # Wait a couple of seconds.
            time.sleep(self.cmd_sleep)

            # Send an "s" command to show current status.
            screen.execute({'s': ''})

            # Wain a second.
            time.sleep(1)
        elif action == 'stop':
            # Send an "s" command to show current status.
            screen.execute({'s': ''})

            # Wain a second.
            time.sleep(1)

            # Hashcat only needs 'q' to pause.
            screen.execute({'q': ''})
        elif action == 'restore':
            if self.__is_past_date(session['terminate_at']):
                return False

            # To restore a session we need a command line like 'hashcat --session NAME --restore'.
            command = self.hashcat.build_restore_command(session['screen_name'])
            screen.execute(command)

            # Wait a couple of seconds.
            time.sleep(self.cmd_sleep)

            # Send an "s" command to show current status.
            screen.execute({'s': ''})

            # Wain a second.
            time.sleep(1)
        else:
            return False

        return True

    def __save_hashcat_history(self, session_id):
        record = HashcatModel.query.filter(HashcatModel.session_id == session_id).first()
        new_record = HashcatHistoryModel(
            session_id=record.session_id,
            mode=record.mode,
            hashtype=record.hashtype,
            wordlist=record.wordlist,
            rule=record.rule,
            mask=record.mask,
            increment_min=record.increment_min,
            increment_max=record.increment_max,
            created_at=datetime.datetime.now(),
        )

        db.session.add(new_record)
        db.session.commit()
        # In order to get the created object, we need to refresh it.
        db.session.refresh(new_record)
        return True

    def get_hashcat_status(self, user_id, session_id):
        screen_log_file = self.session_filesystem.find_latest_screenlog(user_id, session_id)
        stream = self.session_filesystem.tail_file(screen_log_file, 4096)
        if len(stream) == 0:
            return {}

        # Pass to hashcat class to parse and return a dict with all the data.
        data = self.hashcat.parse_stream(stream)

        return data

    def download_file(self, session_id, which_file):
        session = self.get(session_id=session_id)[0]

        save_as = session['name']
        if which_file == 'cracked':
            file = self.session_filesystem.get_crackedfile_path(session['user_id'], session_id)
            save_as = save_as + '.cracked'
        elif which_file == 'hashes':
            file = self.session_filesystem.get_hashfile_path(session['user_id'], session_id)
            save_as = save_as + '.hashes'
        else:
            return 'Error'

        if not os.path.exists(file):
            return 'Error'

        return send_file(file, attachment_filename=save_as, as_attachment=True)

    def get_running_processes(self):
        sessions = self.get()

        data = {
            'stats': {
                'all': 0,
                'web': 0,
                'ssh': 0
            },
            'commands': {
                'all': [],
                'web': [],
                'ssh': []
            }
        }

        processes = self.hashcat.get_running_processes_commands()

        data['stats']['all'] = len(processes)
        data['commands']['all'] = processes

        for process in processes:
            name = self.hashcat.extract_session_from_process(process)
            found = False
            for session in sessions:
                if session['screen_name'] == name:
                    found = True
                    break

            key = 'web' if found else 'ssh'
            data['stats'][key] = data['stats'][key] + 1
            data['commands'][key].append(process)

        return data

    def set_termination_datetime(self, session_id, date, time):
        date_string = date + ' ' + time

        # Check if the format is valid.
        try:
            fulldate = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M')
        except ValueError:
            return False

        if self.__is_past_date(fulldate):
            return False

        session = self.__get_by_id(session_id)
        session.terminate_at = fulldate
        db.session.commit()
        # In order to get the created object, we need to refresh it.
        db.session.refresh(session)

        return True

    def __is_past_date(self, date):
        return datetime.datetime.now() > date

    def terminate_past_sessions(self):
        # Get all sessions which have terminate_at set as a past datetime.
        print("Trying to get past sessions...")
        past_sessions = SessionModel.query.filter(SessionModel.terminate_at < datetime.datetime.now()).all()
        for past_session in past_sessions:
            # Check if session is currently running.
            print("Loading session %d" % past_session.id)
            session = self.get(past_session.user_id, past_session.id)
            if len(session) == 0:
                print("Session %d does not exist" % past_session.id)
                continue
            print("Session % loaded" % past_session.id)
            session = session[0]

            status = session['hashcat']['data']['process_state']
            if status == 1 or status == 4:
                # If it's running or paused, terminate.
                print("Terminating session %d" % past_session.id)
                self.hashcat_action(session['id'], 'stop')

    def guess_hashtype(self, user_id, session_id):
        hashfile = self.session_filesystem.get_hashfile_path(user_id, session_id)
        if not os.path.isfile(hashfile):
            return []

        # Get the first hash from the file
        with open(hashfile, 'r') as f:
            hash = f.readline().strip()

        return self.hashid.guess(hash)
