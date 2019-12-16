from app import db
import datetime


class HashcatModel(db.Model):
    __tablename__ = 'hashcat'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, default=0, index=True, nullable=False)
    mode = db.Column(db.Integer, default=0, index=True, nullable=False)
    hashtype = db.Column(db.String, default='', index=True, nullable=False)
    wordlist = db.Column(db.String, default='', index=True, nullable=False)
    rule = db.Column(db.String, default='', index=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())


class UsedWordlistModel(db.Model):
    __tablename__ = 'used_wordlists'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, default=0, index=True, nullable=False)
    wordlist = db.Column(db.String, default='', index=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
