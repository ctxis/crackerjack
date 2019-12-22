from app import db
import datetime


class ApiKeys(db.Model):
    __tablename__ = 'api_keys'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0, index=True)
    name = db.Column(db.String, default='', nullable=True)
    apikey = db.Column(db.String, default='', nullable=True)
    enabled = db.Column(db.Boolean, default=False, index=True, nullable=True)
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.datetime.now())
