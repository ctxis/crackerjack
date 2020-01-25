import datetime
import json
from app import db
from app.lib.models.webpush import WebPushSubscriptionModel, WebPushLogModel
from pywebpush import webpush, WebPushException


class WebPushManager:
    def __init__(self, vapid_private, admin_email, icon):
        self.vapid_private = vapid_private
        self.admin_email = admin_email
        self.icon = icon

    def register(self, user_id, endpoint, key, authsecret):
        subscription = WebPushSubscriptionModel(
            user_id=user_id,
            endpoint=endpoint,
            key=key,
            authsecret=authsecret,
            finished_at=datetime.datetime.now()
        )

        db.session.add(subscription)
        db.session.commit()
        db.session.refresh(subscription)

        return subscription

    def send(self, user_id, title, body, url):
        subscriptions = WebPushSubscriptionModel.query.filter(WebPushSubscriptionModel.user_id == user_id).all()
        if not subscriptions:
            # User has no subscriptions, therefore no need to raise any errors.
            return True

        for subscription in subscriptions:
            data = {
                'title': title,
                'body': body,
                'url': url,
                'icon': self.icon
            }

            result = self.__send(data, subscription.endpoint, subscription.key, subscription.authsecret)
            if result:
                # Save notification details.
                self.__log_notification(user_id, data)

        return True

    def __log_notification(self, user_id, data):
        log = WebPushLogModel(
            user_id=user_id,
            data=json.dumps(data),
            sent_at=datetime.datetime.now()
        )

        db.session.add(log)
        db.session.commit()
        db.session.refresh(log)

        return log

    def __send(self, data, endpoint, key, authsecret):
        try:
            webpush(
                subscription_info={
                    'endpoint': endpoint,
                    'keys': {
                        'p256dh': key,
                        'auth': authsecret
                    },
                    'contentEncoding': 'aesgcm'
                },
                data=json.dumps(data),
                vapid_private_key=self.vapid_private,
                vapid_claims={
                    'sub': 'mailto:' + self.admin_email
                }
            )

            return True
        except WebPushException as ex:
            print("Error sending push notification: {}", repr(ex))
            if ex.response and ex.response.json():
                extra = ex.response.json()
                print("Remote service replied with a {}:{}, {}",
                      extra.code,
                      extra.errno,
                      extra.message
                      )

        return False
