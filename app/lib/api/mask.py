from app.lib.api.base import ApiBase
from app.lib.base.provider import Provider


class ApiMask(ApiBase):
    def set_mask(self, user_id, session_id):
        required_fields = ['mask']
        data = self.get_json(required_fields)
        if data is False:
            return self.send_error_response(5000, 'Missing fields',
                                            'Required fields are: ' + ', '.join(required_fields))

        provider = Provider()
        sessions = provider.sessions()

        session = sessions.get(user_id=user_id, session_id=session_id)
        if not session:
            return self.send_access_denied_response()

        sessions.set_hashcat_setting(session_id, 'mask', data['mask'])

        return self.send_success_response()

    def set_increment(self, user_id, session_id):
        required_fields = ['state', 'min', 'max']
        data = self.get_json(required_fields)
        if data is False:
            return self.send_error_response(5000, 'Missing fields',
                                            'Required fields are: ' + ', '.join(required_fields))

        provider = Provider()
        sessions = provider.sessions()

        session = sessions.get(user_id=user_id, session_id=session_id)
        if not session:
            return self.send_access_denied_response()

        enable_increments = True if data['state'] else False
        increment_min = int(data['min'])
        increment_max = int(data['max'])

        if enable_increments:
            if increment_min <= 0:
                return self.send_error_response(5006, 'Min Increment is invalid', '')
            elif increment_max <= 0:
                return self.send_error_response(5006, 'Max Increment is invalid', '')
            elif increment_min > increment_max:
                return self.send_error_response(5006, 'Min Increment cannot be bigger than Max Increment', '')
        else:
            increment_min = 0
            increment_max = 0

        sessions.set_hashcat_setting(session_id, 'increment_min', increment_min)
        sessions.set_hashcat_setting(session_id, 'increment_max', increment_max)

        return self.send_success_response()
