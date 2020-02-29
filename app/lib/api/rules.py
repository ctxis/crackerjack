from app.lib.api.base import ApiBase
from app.lib.base.provider import Provider


class ApiRules(ApiBase):
    def get(self):
        provider = Provider()
        rules = provider.rules()

        files = rules.get_rules()

        api_files = []
        for name, file in files.items():
            api_files.append(self.compile_file_object(file))

        return self.send_valid_response(api_files)

    def set(self, user_id, session_id):
        required_fields = ['name']
        data = self.get_json(required_fields)
        if data is False:
            return self.send_error_response(5000, 'Missing fields',
                                            'Required fields are: ' + ', '.join(required_fields))

        provider = Provider()
        sessions = provider.sessions()
        rules = provider.rules()

        session = sessions.get(user_id=user_id, session_id=session_id)
        if not session:
            return self.send_access_denied_response()
        elif not rules.is_valid_rule(data['name']):
            return self.send_error_response(5009, 'Invalid rule', '')

        rule_location = rules.get_rule_path(data['name'])
        sessions.set_hashcat_setting(session_id, 'rule', rule_location)

        return self.send_success_response()
