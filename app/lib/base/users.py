from sqlalchemy import desc, and_, func
from app.lib.models.user import UserModel, UserLogins
from app import db
import flask_bcrypt as bcrypt
import datetime
import random
import string


class UserManager:
    def __init__(self, password_complexity):
        self.last_error = ''
        self.password_complexity = password_complexity

    def __error(self, message):
        self.last_error = message

    def get_last_error(self):
        return self.last_error

    def save(self, user_id, username, password, full_name, email, admin, ldap, active):
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
            user.active = True if active == 1 else False
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
                if not self.password_complexity.meets_requirements(password):
                    self.__error('Password does not meet the complexity requirements: ' + self.password_complexity.get_requirement_description())
                    return False

                # If the password is empty, it means it wasn't changed.
                password = bcrypt.generate_password_hash(password)
        else:
            # This is an LDAP user, no point in setting their password.
            password = ''

        if ldap == 0:
            # There is no point in updating these if it's an LDAP user.
            user.username = username
            if len(password) > 0:
                user.password = password
            user.full_name = full_name
            user.email = email

        user.admin = True if admin == 1 else False
        user.ldap = True if ldap == 1 else False
        user.active = True if active == 1 else False

        if user_id == 0:
            db.session.add(user)

        db.session.commit()
        db.session.refresh(user)

        return True

    def get_by_username(self, username):
        return UserModel.query.filter(and_(func.lower(UserModel.username) == func.lower(username))).first()

    def get_ldap_user(self, username):
        return UserModel.query.filter(and_(func.lower(UserModel.username) == func.lower(username), UserModel.ldap == 1)).first()

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

    def record_login(self, user_id):
        login = UserLogins(user_id=user_id, login_at=datetime.datetime.now())
        db.session.add(login)
        db.session.commit()
        return True

    def get_user_logins(self, user_id):
        conditions = and_(1 == 1)
        if user_id > 0:
            conditions = and_(UserLogins.user_id == user_id)

        logins = UserLogins.query\
            .join(UserModel, UserLogins.user_id == UserModel.id)\
            .add_columns(UserLogins.id, UserLogins.login_at, UserModel.username)\
            .filter(conditions)\
            .order_by(desc(UserLogins.id))\
            .all()

        return logins

    def get_admins(self, only_active):
        conditions = and_(UserModel.admin == 1)
        if only_active:
            conditions = and_(UserModel.admin == 1, UserModel.active == 1)

        return UserModel.query.filter(conditions).order_by(UserModel.id).all()

    def login_session(self, user):
        user.session_token = ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=64))
        return user

    def logout_session(self, user_id):
        user = self.get_by_id(user_id)
        user.session_token = ''
        db.session.commit()
        db.session.refresh(user)
        return True

    def create_ldap_user(self, username, full_name, email):
        user = UserModel.query.filter(and_(UserModel.username == username, UserModel.ldap == 1)).first()
        if not user:
            user = UserModel(
                username=username,
                password='',
                full_name=full_name,
                email=email,
                ldap=True,
                admin=False
            )

            db.session.add(user)
        else:
            user.full_name = full_name
            user.email = email

        db.session.commit()
        # In order to get the created object, we need to refresh it.
        db.session.refresh(user)

        return user