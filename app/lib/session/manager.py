import re
import random
import string
import os
import datetime
from app.lib.models.sessions import SessionModel
from app.lib.models.user import UserModel
from app.lib.models.hashcat import HashcatModel, UsedWordlistModel
from app.lib.session.filesystem import SessionFileSystem
from app import db
from sqlalchemy import and_, desc
from flask import send_file


class SessionManager:
    def __init__(self, hashcat, screens, wordlists, hashid):
        self.hashcat = hashcat
        self.screens = screens
        self.wordlists = wordlists
        self.hashid = hashid
        self.session_filesystem = SessionFileSystem()

    def sanitise_name(self, name):
        return re.sub(r'\W+', '', name)

    def generate_name(self, prefix=''):
        return prefix + ''.join(random.choice(string.ascii_letters + string.digits) for i in range(12))

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
            tail_screen = self.session_filesystem.tail_file(self.session_filesystem.get_screenfile_path(session.user_id, session.id), 4096).decode()

            item = {
                'id': session.id,
                'name': session.name,
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
                    'data': self.process_hashcat_raw_data(hashcat_data_raw, session.screen_name, tail_screen),
                    'hashfile': self.session_filesystem.get_hashfile_path(session.user_id, session.id),
                    'hashfile_exists': self.session_filesystem.hashfile_exists(session.user_id, session.id)
                },
                'user': {
                    'record': UserModel.query.filter(UserModel.id == session.user_id).first()
                },
                'tail_screen': tail_screen,
                'hashes_in_file': self.session_filesystem.count_non_empty_lines_in_file(self.session_filesystem.get_hashfile_path(session.user_id, session.id)),
                'guess_hashtype': self.guess_hashtype(session.user_id, session.id)
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
            if record.wordlist != value and record.wordlist != '':
                used = UsedWordlistModel(
                    session_id=session_id,
                    wordlist=record.wordlist
                )
                db.session.add(used)

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

    def is_process_running(self, screen_name):
        screens = self.hashcat.get_process_screen_names()
        return screen_name in screens

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
        elif action == 'pause':
            # Hashcat only needs 'p' to pause.
            screen.execute({'p': ''})
        elif action == 'stop':
            # Hashcat only needs 'q' to pause.
            screen.execute({'q': ''})
        elif action == 'restore':
            if self.__is_past_date(session['terminate_at']):
                return False

            # To restore a session we need a command line like 'hashcat --session NAME --restore'.
            command = self.hashcat.build_restore_command(session['screen_name'])
            screen.execute(command)
        else:
            return False

        return True

    def get_used_wordlists(self, session_id):
        return UsedWordlistModel.query.filter(UsedWordlistModel.session_id == session_id).all()

    def __detect_session_status(self, raw, screen_name, tail_screen):
        # States are:
        #   0   NOT_STARTED
        #   1   RUNNING
        #   2   STOPPED
        #   3   FINISHED
        #   4   PAUSED
        #   5   CRACKED
        #   98  ERROR
        #   99  UNKNOWN
        status = 0
        if 'Status' in raw:
            if raw['Status'] == 'Running':
                status = 1
                # However, if there's no process then it's probably an error.
                if not self.is_process_running(screen_name):
                    # Set to error.
                    status = 98
            elif raw['Status'] == 'Quit':
                status = 2
            if raw['Status'] == 'Exhausted':
                status = 3
            elif raw['Status'] == 'Paused':
                status = 4
            elif raw['Status'] == 'Cracked':
                status = 5
        else:
            # There's a chance that there's no 'status' output displayed yet. In this case, check if the process is running.
            if self.is_process_running(screen_name):
                # Set to running.
                status = 1

        # If it is STILL not running, take the last few output lines, and mark this as an 'error'.
        if status == 0 and len(tail_screen) > 0:
            status = 98

        return status

    def process_hashcat_raw_data(self, raw, screen_name, tail_screen):
        # Build base dictionary
        data = {
            'process_state': self.__detect_session_status(raw, screen_name, tail_screen),
            'all_passwords': 0,
            'cracked_passwords': 0,
            'time_remaining': '',
            'estimated_completion_time': '',
            'progress': 0
        }

        # progress
        if 'Progress' in raw:
            matches = re.findall('\((\d+.\d+)', raw['Progress'])
            if len(matches) == 1:
                data['progress'] = matches[0]

        # passwords
        if 'Recovered' in raw:
            matches = re.findall('(\d+/\d+)', raw['Recovered'])
            if len(matches) > 0:
                passwords = matches[0].split('/')
                if len(passwords) == 2:
                    data['all_passwords'] = int(passwords[1])
                    data['cracked_passwords'] = int(passwords[0])

        # time remaining
        if 'Time.Estimated' in raw:
            matches = re.findall('\((.*)\)', raw['Time.Estimated'])
            if len(matches) == 1:
                data['time_remaining'] = 'Finished' if matches[0] == '0 secs' else matches[0].strip()

        # estimated completion time
        if 'Time.Estimated' in raw:
            matches = re.findall('(.*)\(', raw['Time.Estimated'])
            if len(matches) == 1:
                data['estimated_completion_time'] = matches[0].strip()

        return data

    def get_hashcat_status(self, user_id, session_id):
        screen_log_file = self.session_filesystem.get_screenfile_path(user_id, session_id)
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
