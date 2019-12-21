from app.lib.models.user import UserModel
from app import db
#import bcrypt
import flask_bcrypt as bcrypt


class UserManager:
    def __init__(self):
        self.last_error = ''

    def __error(self, message):
        self.last_error = message

    def get_last_error(self):
        return self.last_error

    def save(self, user_id, username, password, first_name, last_name, email, admin, ldap):
        if user_id > 0:
            # This is a user-edit.
            user = self.get_by_id(user_id)
            if user is None:
                self.__error('Invalid User ID')
                return False
        else:
            # This is user creation.
            user = UserModel()

        # If it's an existing user and it's the LDAP status that has changed, update only that and return
        # because otherwise it will clear the fields (as the fields are not posted during the submit.
        if user_id > 0 and user.ldap != ldap:
            user.ldap = True if ldap == 1 else False
            db.session.commit()
            db.session.refresh(user)
            return True

        # If there was a username update, check to see if the new username already exists.
        if username != user.username:
            u = self.get_by_username(username)
            if u:
                self.__error('Username already exists')
                return False

        if ldap == 0:
            if password != '':
                # If the password is empty, it means it wasn't changed.
                password = bcrypt.generate_password_hash(password)
        else:
            # This is an LDAP user, no point in setting their password.
            password = ''

        if ldap == 0:
            # There is no point in updating these if it's an LDAP user.
            user.username = username
            user.password = password
            user.first_name = first_name
            user.last_name = last_name
            user.email = email

        user.admin = True if admin == 1 else False
        user.ldap = True if ldap == 1 else False

        if user_id == 0:
            db.session.add(user)

        db.session.commit()
        db.session.refresh(user)

        return True

    def get_by_username(self, username):
        return UserModel.query.filter(UserModel.username == username).first()

    def get_by_id(self, user_id):
        return UserModel.query.filter(UserModel.id == user_id).first()

    def update_password(self, user_id, password):
        user = self.get_by_id(user_id)
        if user is None:
            self.__error('Invalid User ID')
            return False

        password = bcrypt.generate_password_hash(password)
        user.password = password

        db.session.commit()
        db.session.refresh(user)

        return True

    def validate_password(self, hash, password):
        return bcrypt.check_password_hash(hash, password)

    def validate_user_password(self, user_id, password):
        user = self.get_by_id(user_id)
        if not user:
            return False

        return bcrypt.check_password_hash(user.password, password)

    def get_user_count(self):
        return db.session.query(UserModel).count()
