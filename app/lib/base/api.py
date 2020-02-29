import random
import string
from sqlalchemy import and_
from app.lib.models.api import ApiKeys
from app import db


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
