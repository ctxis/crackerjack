import json
from flask import request
from app.lib.api.definitions.response import Response
from app.lib.api.definitions.file import File


class ApiBase:
    def send_valid_response(self, object):
        return self.toJSON(object), 200

    def send_success_response(self):
        response = Response()
        response.success = True
        response.message = 'OK'

        return self.send_valid_response(response)

    def send_access_denied_response(self):
        response = Response()
        response.success = False
        response.message = 'Access Denied'

        return self.toJSON(response), 401

    def send_error_response(self, code, message, details):
        response = Response()
        response.success = False
        response.code = code
        response.message = message
        response.details = details

        return self.toJSON(response), 500

    def toJSON(self, object):
        return json.dumps(object, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def get_json(self, required_fields):
        if not request.is_json:
            return False

        data = request.get_json()
        for field in required_fields:
            if field not in data:
                return False

        return data

    def compile_file_object(self, file):
        api_file = File()

        api_file.name = file['name']
        api_file.size = file['size']

        return api_file
