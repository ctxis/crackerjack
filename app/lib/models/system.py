from app import db
import datetime


class ShellLogModel(db.Model):
    __tablename__ = 'shell_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0, index=True, nullable=True)
    command = db.Column(db.Text, nullable=True)
    output = db.Column(db.Text, nullable=True)
    executed_at = db.Column(db.DateTime, nullable=True, default=datetime.datetime.now())
    finished_at = db.Column(db.DateTime, nullable=True)
