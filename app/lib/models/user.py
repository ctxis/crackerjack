from app import db, login
from flask_login import UserMixin
import datetime


class UserModel(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, default='', index=True, unique=True)
    password = db.Column(db.String(255), nullable=False, default='')
    full_name = db.Column(db.String(255), nullable=True, default='')
    email = db.Column(db.String(255), nullable=True, default='')
    session_token = db.Column(db.String(255), nullable=True, index=True, default='')
    ldap = db.Column(db.Boolean, default=False, index=True)
    azure = db.Column(db.Boolean, default=False, index=True)
    admin = db.Column(db.Boolean, default=False, index=True)
    active = db.Column(db.Boolean, default=True, index=True)
    access_token = db.Column(db.String(255), nullable=True, index=True, default='')
    access_token_expiration = db.Column(db.Integer, nullable=True, index=True, default='')

    def get_id(self):
        return str(self.session_token)


class UserSettings(db.Model):
    __tablename__ = 'user_settings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0, index=True)
    name = db.Column(db.String, default='', nullable=True)
    value = db.Column(db.Text, nullable=True)

    __table_args__ = (db.UniqueConstraint('user_id', 'name', name='index_user_settings_user_id_name'),)


class UserLogins(db.Model):
    __tablename__ = 'user_logins'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0, index=True)
    login_at = db.Column(db.DateTime, nullable=True, default=datetime.datetime.now())


@login.user_loader
def load_user(session_token):
    user = UserModel.query.filter_by(session_token=session_token).first()

    if user.azure:
        if len(user.access_token) == 0:
            return None
    return user
