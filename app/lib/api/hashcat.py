from app.lib.api.base import ApiBase
from app.lib.base.provider import Provider
from app.lib.api.definitions.hashtype import HashType


class ApiHashcat(ApiBase):
    def get_types(self):
        provider = Provider()
        hashcat = provider.hashcat()

        supported_hashes = hashcat.get_supported_hashes()
        api_hashes = []
        for type, hashes in supported_hashes.items():
            for code, hash in hashes.items():
                api_hashes.append(self.__compile_hashtype(code, type + ' / ' + hash))

        return self.send_valid_response(api_hashes)

    def set_type(self, user_id, session_id):
        required_fields = ['type']
        data = self.get_json(required_fields)
        if data is False:
            return self.send_error_response(5000, 'Missing fields',
                                            'Required fields are: ' + ', '.join(required_fields))

        provider = Provider()
        sessions = provider.sessions()
        hashcat = provider.hashcat()

        hash_type = str(data['type'])

        session = sessions.get(user_id=user_id, session_id=session_id)
        if not session:
            return self.send_access_denied_response()
        elif not hashcat.is_valid_hash_type(hash_type):
            return self.send_error_response(5003, 'Invalid type selected', '')

        sessions.set_hashcat_setting(session_id, 'hashtype', hash_type)

        return self.send_success_response()

    def set_optimisation(self, user_id, session_id):
        required_fields = ['optimise']
        data = self.get_json(required_fields)
        if data is False:
            return self.send_error_response(5000, 'Missing fields',
                                            'Required fields are: ' + ', '.join(required_fields))

        provider = Provider()
        sessions = provider.sessions()

        session = sessions.get(user_id=user_id, session_id=session_id)
        if not session:
            return self.send_access_denied_response()

        optimised_kernel = True if data['optimise'] else False

        sessions.set_hashcat_setting(session_id, 'optimised_kernel', optimised_kernel)

        return self.send_success_response()

    def set_mode(self, user_id, session_id):
        required_fields = ['mode']
        data = self.get_json(required_fields)
        if data is False:
            return self.send_error_response(5000, 'Missing fields',
                                            'Required fields are: ' + ', '.join(required_fields))

        provider = Provider()
        sessions = provider.sessions()

        session = sessions.get(user_id=user_id, session_id=session_id)
        if not session:
            return self.send_access_denied_response()

        mode = 0
        if data['mode'] == 'wordlist':
            mode = 0
        elif data['mode'] == 'mask':
            mode = 3
        else:
            return self.send_error_response(5004, 'Invalid mode selected', '')

        sessions.set_hashcat_setting(session_id, 'mode', mode)

        return self.send_success_response()

    def __compile_hashtype(self, type, name):
        api_hashtype = HashType()
        api_hashtype.name = name
        api_hashtype.type = type

        return api_hashtype
