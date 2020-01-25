from app import db


class WebPushSubscriptionModel(db.Model):
    __tablename__ = 'webpush_subscriptions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0, index=True, nullable=True)
    endpoint = db.Column(db.String, default='', index=False, nullable=True)
    key = db.Column(db.String, default='', index=False, nullable=True)
    authsecret = db.Column(db.String, default='', index=False, nullable=True)
    finished_at = db.Column(db.DateTime, nullable=True)


class WebPushLogModel(db.Model):
    __tablename__ = 'webpush_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=0, index=True, nullable=True)
    data = db.Column(db.Text, nullable=True)
    sent_at = db.Column(db.DateTime, nullable=True)
