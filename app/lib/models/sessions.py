from app import db
import datetime


class SessionModel(db.Model):
    __tablename__ = 'sessions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0, index=True, nullable=True)
    name = db.Column(db.String, default='', index=True, nullable=True)
    description = db.Column(db.String, default='', index=True, nullable=True)
    screen_name = db.Column(db.String, default='', index=True, nullable=True)
    active = db.Column(db.Boolean, default=False, index=True, nullable=True)
    notifications_enabled = db.Column(db.Boolean, default=False, index=True, nullable=True)
    terminate_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.datetime.now())


class SessionNotificationModel(db.Model):
    __tablename__ = 'session_notifications'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, default=0, index=True, nullable=True)
    cracked = db.Column(db.Integer, default=0, index=True, nullable=True)
    sent_at = db.Column(db.DateTime, nullable=True)
