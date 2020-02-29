from app.lib.api.base import ApiBase
from app.lib.base.provider import Provider


class ApiWordlists(ApiBase):
    def get(self):
        provider = Provider()
        wordlists = provider.wordlists()

        files = wordlists.get_wordlists()

        api_files = []
        for name, file in files.items():
            api_files.append(self.compile_file_object(file))

        return self.send_valid_response(api_files)

    def set_type(self, user_id, session_id):
        required_fields = ['type']
        data = self.get_json(required_fields)
        if data is False:
            return self.send_error_response(5000, 'Missing fields',
                                            'Required fields are: ' + ', '.join(required_fields))

        provider = Provider()
        sessions = provider.sessions()

        session = sessions.get(user_id=user_id, session_id=session_id)
        if not session:
            return self.send_access_denied_response()
        elif not data['type'] in ['global', 'custom', 'cracked']:
            return self.send_error_response(5010, 'Invalid wordlist type', '')

        type = 0
        if data['type'] == 'global':
            type = 0
        elif data['type'] == 'custom':
            type = 1
        elif data['type'] == 'cracked':
            type = 2

        sessions.set_hashcat_setting(session_id, 'wordlist_type', type)

        return self.send_success_response()

    def set_global(self, user_id, session_id):
        required_fields = ['name']
        data = self.get_json(required_fields)
        if data is False:
            return self.send_error_response(5000, 'Missing fields',
                                            'Required fields are: ' + ', '.join(required_fields))

        provider = Provider()
        sessions = provider.sessions()
        wordlists = provider.wordlists()

        session = sessions.get(user_id=user_id, session_id=session_id)
        if not session:
            return self.send_access_denied_response()
        elif not wordlists.is_valid_wordlist(data['name']):
            return self.send_error_response(5009, 'Invalid wordlist', '')

        wordlist_location = wordlists.get_wordlist_path(data['name'])
        sessions.set_hashcat_setting(session_id, 'wordlist', wordlist_location)

        return self.send_success_response()

    def set_custom(self, user_id, session_id):
        required_fields = ['data']
        data = self.get_json(required_fields)
        if data is False:
            return self.send_error_response(5000, 'Missing fields',
                                            'Required fields are: ' + ', '.join(required_fields))

        provider = Provider()
        sessions = provider.sessions()

        session = sessions.get(user_id=user_id, session_id=session_id)
        if not session:
            return self.send_access_denied_response()

        save_as = sessions.session_filesystem.get_custom_wordlist_path(user_id, session_id, prefix='custom_wordlist_', random=True)
        sessions.session_filesystem.write_to_file(save_as, data['data'])
        sessions.set_hashcat_setting(session_id, 'wordlist', save_as)

        return self.send_success_response()

    def set_cracked(self, user_id, session_id):
        provider = Provider()
        sessions = provider.sessions()

        session = sessions.get(user_id=user_id, session_id=session_id)
        if not session:
            return self.send_access_denied_response()

        save_as = sessions.session_filesystem.get_custom_wordlist_path(user_id, session_id, prefix='pwd_wordlist')
        sessions.export_cracked_passwords(session_id, save_as)
        sessions.set_hashcat_setting(session_id, 'wordlist', save_as)

        return self.send_success_response()
