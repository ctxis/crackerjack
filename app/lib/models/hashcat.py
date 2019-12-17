from app import db
import datetime


class HashcatModel(db.Model):
    __tablename__ = 'hashcat'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, default=0, index=True, nullable=True)
    mode = db.Column(db.Integer, default=0, index=True, nullable=True)
    hashtype = db.Column(db.String, default='', index=True, nullable=True)
    wordlist = db.Column(db.String, default='', index=True, nullable=True)
    rule = db.Column(db.String, default='', index=True, nullable=True)
    mask = db.Column(db.String, default='', index=True, nullable=True)
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.datetime.now())


class UsedWordlistModel(db.Model):
    __tablename__ = 'used_wordlists'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, default=0, index=True, nullable=True)
    wordlist = db.Column(db.String, default='', index=True, nullable=True)
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.datetime.now())
