from app import db
import datetime


class SessionModel(db.Model):
    __tablename__ = 'sessions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0, index=True, nullable=False)
    name = db.Column(db.String, default='', index=True, nullable=False)
    screen_name = db.Column(db.String, default='', index=True, nullable=False)
    active = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())