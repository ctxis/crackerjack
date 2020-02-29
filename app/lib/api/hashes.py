from app.lib.api.base import ApiBase
from app.lib.base.provider import Provider


class ApiHashes(ApiBase):
    def upload(self, user_id, session_id):
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

        sessions.session_filesystem.save_hashes(user_id, session_id, data['data'])

        return self.send_success_response()

    def get_remote(self):
        provider = Provider()
        hashes = provider.hashes()

        files = hashes.get_uploaded_hashes()

        api_files = []
        for name, file in files.items():
            api_files.append(self.compile_file_object(file))

        return self.send_valid_response(api_files)

    def set_remote(self, user_id, session_id):
        required_fields = ['file']
        data = self.get_json(required_fields)
        if data is False:
            return self.send_error_response(5000, 'Missing fields',
                                            'Required fields are: ' + ', '.join(required_fields))

        provider = Provider()
        sessions = provider.sessions()
        hashes = provider.hashes()

        session = sessions.get(user_id=user_id, session_id=session_id)
        if not session:
            return self.send_access_denied_response()
        elif not hashes.is_valid_uploaded_hashfile(data['file']):
            return self.send_error_response(5002, 'Invalid file selected', '')

        save_as = sessions.session_filesystem.get_hashfile_path(user_id, session_id)
        local_path = hashes.get_uploaded_hashes_path(data['file'])
        if not hashes.copy_file(local_path, save_as):
            return self.send_error_response(5003, 'Could not copy hashes file to data directory', '')

        return self.send_success_response()

    def download(self, user_id, session_id):
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
        elif not data['type'] in ['all', 'plain', 'cracked']:
            return self.send_error_response(5009, 'Invalid download type', '')

        return sessions.download_file(session_id, data['type'])
