import random
import string
import json
from sqlalchemy import and_
from app.lib.models.api import ApiKeys
from app.lib.models.user import UserModel
from app import db
from flask import request, abort


class ApiManager:
    def __init__(self, sessions):
        self.sessions = sessions

    def create_key(self, user_id, name):
        if len(name) == 0:
            return False

        key = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=32))
        item = ApiKeys(user_id=user_id, name=name, apikey=key, enabled=True)
        db.session.add(item)
        db.session.commit()
        db.session.refresh(item)

        return item

    def get(self, user_id=0):
        conditions = and_(1 == 1)
        if user_id > 0:
            conditions = and_(ApiKeys.user_id == user_id)

        return ApiKeys.query.filter(conditions).all()

    def can_access(self, user, key_id):
        if user.admin:
            return True

        apikey = ApiKeys.query.filter(
            and_(
                ApiKeys.user_id == user.id,
                ApiKeys.id == key_id
            )
        ).first()

        return True if apikey else False

    def set_key_status(self, key_id, value):
        apikey = ApiKeys.query.filter(ApiKeys.id == key_id).first()
        if not apikey:
            return False

        apikey.enabled = value
        db.session.commit()

        return True

    def __auth(self, apikey):
        if len(apikey) == 0:
            return False

        key = ApiKeys.query.filter(and_(ApiKeys.apikey == apikey, ApiKeys.enabled == True)).first()
        if not key:
            return False

        return UserModel.query.filter(UserModel.id == key.user_id).first()

    def create_session(self, user_id, name):
        return self.sessions.create(user_id, name)

    def prep_session_response(self, session):
        # Remove sensitive or non-required parameters.
        del session['user']
        del session['screen_name']
        del session['hashcat']['wordlist_path']
        del session['hashcat']['rule_path']
        del session['hashcat']['hashfile']

        return session

    def prep_wordlist_response(self, wordlists):
        for key, data in wordlists.items():
            del data['path']
            del data['size_human']

        return wordlists

    def prep_rule_response(self, rules):
        for key, data in rules.items():
            del data['path']
            del data['size_human']

        return rules

    def response(self, result, message='', data=None):
        resp = {
            'success': result,
            'message': message,
            'data': '' if data is None else data
        }
        return json.dumps(resp, default=str)

    def auth_api(self):
        apikey = request.headers['X-CrackerJack-Auth'] if 'X-CrackerJack-Auth' in request.headers else ''
        user = self.__auth(apikey)
        if not user:
            abort(403)

        return user

    def get_json(self):
        if not request.is_json:
            abort(400)

        return request.get_json()
