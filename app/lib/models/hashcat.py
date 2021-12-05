from app import db
import datetime


class HashcatModel(db.Model):
    __tablename__ = 'hashcat'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, default=0, index=True, nullable=True)
    mode = db.Column(db.Integer, default=0, index=True, nullable=True)
    workload = db.Column(db.Integer, default=2, index=True, nullable=True)
    hashtype = db.Column(db.String, default='', index=True, nullable=True)
    wordlist_type = db.Column(db.Integer, default=0, index=True, nullable=True)
    wordlist = db.Column(db.String, default='', index=True, nullable=True)
    rule_type = db.Column(db.Integer, default=0, index=True, nullable=True)
    rule = db.Column(db.String, default='', index=True, nullable=True)
    mask = db.Column(db.String, default='', index=True, nullable=True)
    increment_min = db.Column(db.Integer, default=0, index=True, nullable=True)
    increment_max = db.Column(db.Integer, default=0, index=True, nullable=True)
    optimised_kernel = db.Column(db.Boolean, default=False, index=True, nullable=True)
    contains_usernames = db.Column(db.Boolean, default=False, index=True, nullable=True)
    device_profile_id = db.Column(db.Integer, default=0, index=True, nullable=True)
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.datetime.now())


class HashcatHistoryModel(db.Model):
    """
    This table should be identical to the "hashcat" table (see top of this file).
    """
    __tablename__ = 'hashcat_history'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, default=0, index=True, nullable=True)
    mode = db.Column(db.Integer, default=0, index=True, nullable=True)
    workload = db.Column(db.Integer, default=2, index=True, nullable=True)
    hashtype = db.Column(db.String, default='', index=True, nullable=True)
    wordlist_type = db.Column(db.Integer, default=0, index=True, nullable=True)
    wordlist = db.Column(db.String, default='', index=True, nullable=True)
    rule_type = db.Column(db.Integer, default=0, index=True, nullable=True)
    rule = db.Column(db.String, default='', index=True, nullable=True)
    mask = db.Column(db.String, default='', index=True, nullable=True)
    increment_min = db.Column(db.Integer, default=0, index=True, nullable=True)
    increment_max = db.Column(db.Integer, default=0, index=True, nullable=True)
    optimised_kernel = db.Column(db.Boolean, default=False, index=True, nullable=True)
    contains_usernames = db.Column(db.Boolean, default=False, index=True, nullable=True)
    device_profile_id = db.Column(db.Integer, default=0, index=True, nullable=True)
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.datetime.now())


class DeviceProfileModel(db.Model):
    __tablename__ = 'device_profiles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, default='', unique=True, nullable=True)
    devices = db.Column(db.String, default='', nullable=True)
    enabled = db.Column(db.Boolean, default=False, index=True, nullable=True)
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.datetime.now())
