from app import db, login
from flask_login import UserMixin


class UserModel(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, default='', index=True, unique=True)
    password = db.Column(db.String(255), nullable=False, default='')
    first_name = db.Column(db.String(255), nullable=True, default='')
    last_name = db.Column(db.String(255), nullable=True, default='')
    email = db.Column(db.String(255), nullable=True, default='')
    ldap = db.Column(db.Boolean, default=False, index=True)
    admin = db.Column(db.Boolean, default=False, index=True)


class UserSettings(db.Model):
    __tablename__ = 'user_settings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0, index=True)
    name = db.Column(db.String, default='', nullable=True)
    value = db.Column(db.Text, nullable=True)

    __table_args__ = (db.UniqueConstraint('user_id', 'name', name='index_user_settings_user_id_name'),)


@login.user_loader
def load_user(id):
    return UserModel.query.get(int(id))
