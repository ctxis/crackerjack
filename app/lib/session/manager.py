import re
import random
import string
import os
import datetime
import time
from app.lib.models.sessions import SessionModel, SessionNotificationModel
from app.lib.models.hashcat import HashcatModel, HashcatHistoryModel
from app.lib.session.filesystem import SessionFileSystem
from app.lib.session.instance import SessionInstance
from app.lib.hashcat.instance import HashcatInstance
from app import db
from sqlalchemy import and_, desc
from flask import send_file


class SessionManager:
    def __init__(self, hashcat, screens, wordlists, filesystem, webpush, shell, device_profile_manager):
        self.hashcat = hashcat
        self.screens = screens
        self.wordlists = wordlists
        self.filesystem = filesystem
        self.webpush = webpush
        self.shell = shell
        self.session_filesystem = SessionFileSystem(filesystem)
        self.cmd_sleep = 2
        self.device_profile_manager = device_profile_manager

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

    def create(self, user_id, description, prefix):
        prefix = self.sanitise_name(prefix) + '_'
        name = self.generate_name(prefix=prefix, length=4)

        # If it exists (shouldn't), return it.
        session = self.__get(user_id, name, True)
        if session:
            return session

        session = SessionModel(
            user_id=user_id,
            name=name,
            description=description,
            active=True,
            screen_name=''
        )
        db.session.add(session)
        db.session.commit()
        # In order to get the created object, we need to refresh it.
        db.session.refresh(session)

        # We need to append the session_id to the session name.
        name = name + '_' + str(session.id)
        session.name = name
        session.screen_name = self.__generate_screen_name(user_id, name)

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

    def can_access_history(self, user, session_id, history_id):
        if user.admin:
            return True

        history = HashcatHistoryModel.query.filter(
            and_(
                HashcatHistoryModel.id == history_id,
                HashcatHistoryModel.session_id == session_id
            )
        ).first()

        return True if history else False

    def get(self, user_id=0, session_id=0, active=None):
        query = SessionModel.query
        if user_id > 0:
            query = query.filter(SessionModel.user_id == user_id)

        if session_id > 0:
            query = query.filter(SessionModel.id == session_id)

        if active is not None:
            query = query.filter(SessionModel.active == active)

        sessions = query.all()

        data = []
        for session in sessions:
            hashcat_instance = HashcatInstance(session, self.session_filesystem, self.hashcat, self.wordlists, self.device_profile_manager)
            instance = SessionInstance(session, hashcat_instance, self.session_filesystem)
            data.append(instance)

        return data

    def restore_hashcat_history(self, session_id, history_id):
        history = HashcatHistoryModel.query.filter(HashcatHistoryModel.id == history_id).first()
        current = HashcatModel.query.filter(HashcatModel.session_id == session_id).first()

        if not history or not current:
            return False

        current.mode = history.mode
        current.hashtype = history.hashtype
        current.wordlist_type = history.wordlist_type
        current.wordlist = history.wordlist
        current.rule_type = history.rule_type
        current.rule = history.rule
        current.mask_type = history.mask_type
        current.masklist = history.masklist
        current.mask = history.mask
        current.increment_min = history.increment_min
        current.increment_max = history.increment_max
        current.optimised_kernel = history.optimised_kernel
        current.contains_usernames = history.contains_usernames
        current.device_profile_id = history.device_profile_id
        current.workload = history.workload

        db.session.commit()
        return True

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
        elif name == 'rule_type':
            record.rule_type = value
        elif name == 'rule':
            record.rule = value
        elif name == 'mask_type':
            record.mask_type = value
        elif name == 'masklist':
            record.masklist = value
        elif name == 'mask':
            record.mask = value
        elif name == 'increment_min':
            record.increment_min = value
        elif name == 'increment_max':
            record.increment_max = value
        elif name == 'optimised_kernel':
            record.optimised_kernel = value
        elif name == 'wordlist_type':
            record.wordlist_type = value
        elif name == 'workload':
            record.workload = value
        elif name == 'contains_usernames':
            record.contains_usernames = value
        elif name == 'device_profile_id':
            record.device_profile_id = value

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

    def export_cracked_passwords(self, session_id, save_as):
        # First get the session.
        session = self.get(session_id=session_id)[0]

        command = self.hashcat.build_export_password_command_line(
            self.session_filesystem.get_hashfile_path(session.user_id, session_id),
            self.session_filesystem.get_potfile_path(session.user_id, session_id),
            save_as,
            session.hashcat.contains_usernames,
            session.hashcat.hashtype
        )
        self.shell.execute(command)

        return True

    def hashcat_action(self, session_id, action):
        # First get the session.
        session = self.get(session_id=session_id)[0]

        # Make sure the screen is running.
        screen = self.screens.get(session.screen_name, log_file=self.session_filesystem.get_screenfile_path(session.user_id, session_id))

        if action == 'start':
            if self.__is_past_date(session.terminate_at):
                return False

            command = self.hashcat.build_command_line(
                session.screen_name,
                int(session.hashcat.mode),
                session.hashcat.mask,
                session.hashcat.hashtype,
                self.session_filesystem.get_hashfile_path(session.user_id, session_id),
                session.hashcat.wordlist_path,
                session.hashcat.rule_path,
                self.session_filesystem.get_crackedfile_path(session.user_id, session_id),
                self.session_filesystem.get_potfile_path(session.user_id, session_id),
                int(session.hashcat.increment_min),
                int(session.hashcat.increment_max),
                int(session.hashcat.optimised_kernel),
                int(session.hashcat.workload),
                int(session.hashcat.contains_usernames),
                session.hashcat.device_list
            )

            # Before we start a new session, rename the previous "screen.log" file
            # so that we can determine errors/state easier.
            self.session_filesystem.backup_screen_log_file(session.user_id, session_id)

            # Even though we renamed the file, as it is still open the OS handle will now point to the renamed file.
            # We re-set the screen logfile to the original file.
            screen.set_logfile(self.session_filesystem.get_screenfile_path(session.user_id, session_id))
            screen.execute(command)

            # Every time we start a session, we make a copy of the settings and put them in the hashcat_history table.
            self.__save_hashcat_history(session_id)
        elif action == 'reset':
            # Close the screen.
            screen.quit()

            # Create it again.
            screen = self.screens.get(session.screen_name, log_file=self.session_filesystem.get_screenfile_path(session.user_id, session_id))
        elif action == 'resume':
            if self.__is_past_date(session.terminate_at):
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
            if self.__is_past_date(session.terminate_at):
                return False

            # To restore a session we need a command line like 'hashcat --session NAME --restore'.
            command = self.hashcat.build_restore_command(session.screen_name)
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
            wordlist_type=record.wordlist_type,
            rule_type=record.rule_type,
            rule=record.rule,
            mask_type=record.mask_type,
            masklist=record.masklist,
            mask=record.mask,
            increment_min=record.increment_min,
            increment_max=record.increment_max,
            optimised_kernel=record.optimised_kernel,
            workload=record.workload,
            contains_usernames=record.contains_usernames,
            device_profile_id=record.device_profile_id,
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

        save_as = session.description
        if which_file == 'cracked':
            file = self.session_filesystem.get_crackedfile_path(session.user_id, session_id)
            save_as = save_as + '.cracked.txt'
        elif which_file == 'hashes' or which_file == 'all':
            file = self.session_filesystem.get_hashfile_path(session.user_id, session_id)
            save_as = save_as + '.hashes.txt'
        elif which_file == 'plain':
            file = self.session_filesystem.get_custom_file_path(session.user_id, session_id, prefix='pwd_wordlist')
            self.export_cracked_passwords(session_id, file)
            save_as = save_as + '.plain.txt'
        else:
            # It means it's a raw/screen log file.
            files = self.get_data_files(session.user_id, session_id)
            if not which_file in files:
                return 'Error'
            file = files[which_file]['path']
            save_as = which_file

        if not os.path.exists(file):
            return 'Error'

        return send_file(file, attachment_filename=save_as, as_attachment=True)

    def get_cracked_passwords(self, session_id):
        session = self.get(session_id=session_id)[0]
        file = self.session_filesystem.get_custom_file_path(session.user_id, session_id, prefix='pwd_cracked')
        if os.path.isfile(file):
            os.remove(file)

        self.export_cracked_passwords(session_id, file)

        return self.session_filesystem.read_file(file)

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
                if session.screen_name == name:
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
            print("Session %d loaded" % past_session.id)
            session = session[0]

            status = session.hashcat.state
            if status == 1 or status == 4:
                # If it's running or paused, terminate.
                print("Terminating session %d" % past_session.id)
                self.hashcat_action(session.id, 'stop')

    def guess_hashtype(self, user_id, session_id, contains_username):
        hashfile = self.session_filesystem.get_hashfile_path(user_id, session_id)
        if not os.path.isfile(hashfile):
            return []

        # Get the first hash from the file
        try:
            with open(hashfile, 'r') as f:
                hash = f.readline().strip()

            if contains_username:
                hash = hash.split(':', 1)[1]
        except UnicodeDecodeError:
            hash = ''

        return self.hashcat.guess_hash(hash)

    def get_data_files(self, user_id, session_id):
        user_data_path = self.session_filesystem.get_user_data_path(user_id, session_id)
        return self.filesystem.get_files(user_data_path)

    def set_notifications(self, session_id, enabled):
        session = self.__get_by_id(session_id)
        session.notifications_enabled = enabled

        db.session.commit()

        return True

    def send_notifications(self):
        # Get all sessions with enabled notifications.
        print("Loading sessions with notifications enabled.")
        sessions = SessionModel.query.filter(
            and_(
                SessionModel.active == 1,
                SessionModel.notifications_enabled == 1
            )
        ).all()

        if not sessions or len(sessions) == 0:
            print("No sessions loaded")
            return True

        print("Loaded %d sessions" % len(sessions))
        for session in sessions:
            full_session = self.get(session_id=session.id)[0]
            if not full_session:
                print("Could not get the actual session's details")
                continue

            # Get the currently cracked passwords.
            all_passwords = int(full_session.hashcat.all_passwords)
            cracked = int(full_session.hashcat.cracked_passwords)

            # Get the last sent notification.
            sent = SessionNotificationModel.query.filter(
                SessionNotificationModel.session_id == session.id
            ).order_by(
                desc(SessionNotificationModel.id)
            ).first()
            previously_cracked = sent.cracked if sent else 0

            # Check if the currently cracked passwords are more than the ones previously sent.
            if previously_cracked >= cracked:
                print("Skipping notification - cracked are less or equal than previously cracked")
                continue

            # Send notification.
            title = 'Progress Update'
            body = '%d/%d Hashes Recovered' % (cracked, all_passwords)
            url = '/sessions/%d/view' % session.id

            print("Sending notification to user %d for session %d" % (full_session.user_id, session.id))
            if self.webpush.send(session.user_id, title, body, url):
                print("Notification sent")
                # Save current notification
                log = SessionNotificationModel(
                    session_id=session.id,
                    cracked=cracked,
                    sent_at=datetime.datetime.now()
                )

                db.session.add(log)
                db.session.commit()
            else:
                print("Could not send notification")

        print("Finished sending notifications")
        return True

    def set_active(self, session_id, active):
        session = self.__get_by_id(session_id)
        session.active = active

        db.session.commit()
        db.session.refresh(session)
        return True

    def delete(self, session_id):
        session = self.get(session_id=session_id)
        if not session or len(session) == 0:
            # If we can't get the session, consider it deleted - MIND GAMES!
            return True

        session = session[0]
        if session.hashcat.state in [1, 4]:
            # Session is either running or paused.
            return False

        # Delete data first.
        data_path = self.session_filesystem.get_user_data_path(session.user_id, session.id)
        if os.path.isdir(data_path):
            self.session_filesystem.delete_path(data_path)

        # Now delete database records.
        HashcatModel.query.filter_by(session_id=session.id).delete()
        HashcatHistoryModel.query.filter_by(session_id=session.id).delete()
        SessionNotificationModel.query.filter_by(session_id=session.id).delete()
        SessionModel.query.filter_by(id=session.id).delete()

        db.session.commit()
        return True
