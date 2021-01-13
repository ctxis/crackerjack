from app.lib.api.base import ApiBase
from app.lib.base.provider import Provider
from app.lib.api.definitions.new_session import NewSession
from app.lib.api.definitions.session import Session
from app.lib.api.definitions.hashcat import Hashcat
from app.lib.api.definitions.session_state import SessionState


class ApiSession(ApiBase):
    def create(self, user_id, username):
        required_fields = ['name']
        data = self.get_json(required_fields)
        if data is False:
            return self.send_error_response(5000, 'Missing fields',
                                            'Required fields are: ' + ', '.join(required_fields))

        provider = Provider()
        sessions = provider.sessions()

        session = sessions.create(user_id, data['name'], username)
        if session is None:
            return self.send_error_response(5002, 'Could not create session', '')

        new_session = NewSession()
        new_session.id = session.id

        return self.send_valid_response(new_session)

    def get_all(self, user_id):
        provider = Provider()
        sessions = provider.sessions()

        sessions = sessions.get(user_id=user_id)

        data = []
        for session in sessions:
            api_session = self.__get_api_session(session)
            data.append(api_session)

        return self.send_valid_response(data)

    def get(self, user_id, session_id):
        provider = Provider()
        sessions = provider.sessions()

        session = sessions.get(user_id=user_id, session_id=session_id)
        if not session:
            return self.send_access_denied_response()

        api_session = self.__get_api_session(session[0])
        return self.send_valid_response(api_session)

    def can_access(self, user, session_id):
        provider = Provider()
        sessions = provider.sessions()
        return sessions.can_access(user, session_id)

    def validate(self, user_id, session_id):
        provider = Provider()
        sessions = provider.sessions()

        session = sessions.get(user_id=user_id, session_id=session_id)
        if not session:
            return self.send_access_denied_response()

        api_session = self.__get_api_session(session[0])

        return self.send_valid_response(api_session.validation)

    def state(self, user_id, session_id):
        provider = Provider()
        sessions = provider.sessions()

        session = sessions.get(user_id=user_id, session_id=session_id)
        if not session:
            return self.send_access_denied_response()

        api_session = self.__get_api_session(session[0])

        session_state = SessionState()
        session_state.state = api_session.hashcat.state
        session_state.description = api_session.hashcat.state_description
        session_state.progress = api_session.hashcat.progress

        return self.send_valid_response(session_state)

    def termination(self, user_id, session_id):
        required_fields = ['date', 'time']
        data = self.get_json(required_fields)
        if data is False:
            return self.send_error_response(5000, 'Missing fields',
                                            'Required fields are: ' + ', '.join(required_fields))

        provider = Provider()
        sessions = provider.sessions()

        session = sessions.get(user_id=user_id, session_id=session_id)
        if not session:
            return self.send_access_denied_response()

        if not sessions.set_termination_datetime(session_id, data['date'], data['time']):
            return self.send_error_response(5007, 'Invalid termination date/time entered', '')

        return self.send_success_response()

    def notifications(self, user_id, session_id):
        required_fields = ['state']
        data = self.get_json(required_fields)
        if data is False:
            return self.send_error_response(5000, 'Missing fields',
                                            'Required fields are: ' + ', '.join(required_fields))

        provider = Provider()
        sessions = provider.sessions()

        session = sessions.get(user_id=user_id, session_id=session_id)
        if not session:
            return self.send_access_denied_response()

        notifications_enabled = True if data['state'] else False
        sessions.set_notifications(session_id, notifications_enabled)

        return self.send_success_response()

    def action(self, user_id, session_id):
        required_fields = ['action']
        data = self.get_json(required_fields)
        if data is False:
            return self.send_error_response(5000, 'Missing fields',
                                            'Required fields are: ' + ', '.join(required_fields))

        provider = Provider()
        sessions = provider.sessions()

        session = sessions.get(user_id=user_id, session_id=session_id)
        if not session:
            return self.send_access_denied_response()
        elif not data['action'] in ['start', 'stop', 'pause', 'rebuild', 'restore']:
            return self.send_error_response(5007, 'Invalid action to execute', '')

        # This is the current state.
        state = session[0].hashcat.state

        result = False
        if data['action'] == 'start':
            result = sessions.hashcat_action(session_id, 'start')
        elif data['action'] == 'stop':
            # Execute only if session is currently running or is paused.
            if state == 1 or state == 4:
                result = sessions.hashcat_action(session_id, 'stop')
        elif data['action'] == 'pause':
            # Execute only if session is running.
            if state == 1:
                result = sessions.hashcat_action(session_id, 'pause')
        elif data['action'] == 'resume':
            # Execute only if session is paused.
            if state == 4:
                result = sessions.hashcat_action(session_id, 'resume')
        elif data['action'] == 'rebuild':
            # Execute only if session is not running or is paused.
            if state != 1 and state != 4:
                result = sessions.hashcat_action(session_id, 'reset')
        elif data['action'] == 'restore':
            # Execute only if session is not running or is paused.
            if state != 1 and state != 4:
                result = sessions.hashcat_action(session_id, 'restore')

        if result is False:
            return self.send_error_response(5008, 'Could not execute action', '')

        return self.state(user_id, session_id)

    def __get_api_session(self, session):
        api_hashcat = self.__compile_hashcat_object(session)
        api_session = self.__compile_session_object(session)
        api_session.hashcat = api_hashcat

        return api_session

    def __compile_hashcat_object(self, session):
        api_hashcat = Hashcat()

        api_hashcat.state = session.hashcat.state
        api_hashcat.state_description = session.hashcat.state_description
        api_hashcat.crackedPasswords = session.hashcat.cracked_passwords
        api_hashcat.allPasswords = session.hashcat.all_passwords
        api_hashcat.progress = session.hashcat.progress
        api_hashcat.timeRemaining = session.hashcat.time_remaining
        api_hashcat.estimatedCompletionTime = session.hashcat.estimated_completion_time
        api_hashcat.dataRaw = session.hashcat.data_raw
        api_hashcat.data = session.hashcat.data
        api_hashcat.incrementMin = session.hashcat.increment_min
        api_hashcat.incrementMax = session.hashcat.increment_max
        api_hashcat.incrementEnabled = session.hashcat.increment_enabled
        api_hashcat.mode = session.hashcat.mode
        api_hashcat.hashType = session.hashcat.hashtype
        api_hashcat.wordlistType = session.hashcat.wordlist_type
        api_hashcat.wordlist = session.hashcat.wordlist
        api_hashcat.rule = session.hashcat.rule
        api_hashcat.mask = session.hashcat.mask
        api_hashcat.optimisedKernel = session.hashcat.optimised_kernel

        return api_hashcat

    def __compile_session_object(self, session):
        api_session = Session()

        api_session.id = session.id
        api_session.description = session.description
        api_session.name = session.name
        api_session.username = session.username
        api_session.terminateAt = session.terminate_at.strftime('%Y-%m-%d %H:%M') if session.terminate_at else ''
        api_session.userId = session.user_id
        api_session.screenName = session.screen_name
        api_session.active = session.active
        api_session.notificationEnabled = session.notifications_enabled
        api_session.createdAt = session.created_at.strftime('%Y-%m-%d %H:%M')
        api_session.friendlyName = session.friendly_name
        api_session.hashesInFile = session.hashes_in_file
        api_session.hashFileExists = session.hashfile_exists
        api_session.validation = session.validation

        return api_session
