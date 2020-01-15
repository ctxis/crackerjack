import ldap3
from sqlalchemy import and_
from app.lib.models.user import UserModel
from app import db


class LDAPManager:
    def __init__(self):
        self._enabled = 0
        self._host = ''
        self._base_dn = ''
        self._domain = ''
        self._bind_user = ''
        self._bind_pass = ''
        self._mapping_username = ''
        self._mapping_firstname = ''
        self._mapping_lastname = ''
        self._mapping_email = ''
        self._ssl = 0

    @property
    def ssl(self):
        return self._ssl

    @ssl.setter
    def ssl(self, value):
        self._ssl = int(value)

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = int(value)

    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        self._host = value

    @property
    def base_dn(self):
        return self._base_dn

    @base_dn.setter
    def base_dn(self, value):
        self._base_dn = value

    @property
    def domain(self):
        return self._domain

    @domain.setter
    def domain(self, value):
        self._domain = value

    @property
    def bind_user(self):
        return self._bind_user

    @bind_user.setter
    def bind_user(self, value):
        self._bind_user = value

    @property
    def bind_pass(self):
        return self._bind_pass

    @bind_pass.setter
    def bind_pass(self, value):
        self._bind_pass = value

    @property
    def mapping_username(self):
        return self._mapping_username

    @mapping_username.setter
    def mapping_username(self, value):
        self._mapping_username = value

    @property
    def mapping_firstname(self):
        return self._mapping_firstname

    @mapping_firstname.setter
    def mapping_firstname(self, value):
        self._mapping_firstname = value

    @property
    def mapping_lastname(self):
        return self._mapping_lastname

    @mapping_lastname.setter
    def mapping_lastname(self, value):
        self._mapping_lastname = value

    @property
    def mapping_email(self):
        return self._mapping_email

    @mapping_email.setter
    def mapping_email(self, value):
        self._mapping_email = value

    def is_enabled(self):
        return self._enabled > 0

    def authenticate(self, username, password, auto_create_user=False):
        server = ldap3.Server(self._host, get_info=ldap3.ALL, use_ssl=self._ssl)
        user = self._domain + "\\" + username
        conn = ldap3.Connection(server, user=user, password=password, authentication=ldap3.NTLM)
        result = conn.bind()
        if result:
            conn.unbind()

        if auto_create_user:
            self.load_user(username)

        return result

    def __create_user(self, username, first_name, last_name, email):
        user = UserModel.query.filter(and_(UserModel.username == username, UserModel.ldap == 1)).first()
        if not user:
            user = UserModel(
                username=username,
                password='',
                first_name=first_name,
                last_name=last_name,
                email=email,
                ldap=True,
                admin=False
            )

            db.session.add(user)
        else:
            user.first_name = first_name
            user.last_name = last_name
            user.email = email

        db.session.commit()
        # In order to get the created object, we need to refresh it.
        db.session.refresh(user)

        return user

    def load_user(self, username):
        server = ldap3.Server(self._host, get_info=ldap3.ALL)
        user = self._domain + "\\" + self._bind_user
        conn = ldap3.Connection(server, user=user, password=self._bind_pass, authentication=ldap3.NTLM)
        result = conn.bind()
        if not result:
            return False

        # Mandatory fields
        attributes = [self._mapping_username, self._mapping_firstname]

        # Optional fields
        if len(self._mapping_lastname) > 0:
            attributes.append(self._mapping_lastname)

        if len(self._mapping_email) > 0:
            attributes.append(self._mapping_email)

        conn.search(self._base_dn, "(&(objectclass=person)(" + self.mapping_username + "=" + username + "))", attributes=attributes)
        if len(conn.entries) != 1:
            return False

        return self.__create_user(
            conn.entries[0][self._mapping_username].value,
            conn.entries[0][self._mapping_firstname].value,
            conn.entries[0][self._mapping_lastname].value if len(self._mapping_lastname) > 0 else '',
            conn.entries[0][self._mapping_email].value if len(self._mapping_email) > 0 else ''
        )
