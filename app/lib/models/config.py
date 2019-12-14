from app import db


class ConfigModel(db.Model):
    __tablename__ = 'config'
    name = db.Column(db.String, default='', primary_key=True)
    value = db.Column(db.Text, default='')