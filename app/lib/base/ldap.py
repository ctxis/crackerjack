import ldap3
from ldap3.core.exceptions import LDAPSocketSendError, LDAPSocketOpenError
from ldap3.extend.microsoft.modifyPassword import ad_modify_password


class LDAPManager:
    AUTH_INVALID_LOGIN = -1
    AUTH_SUCCESS = 0
    AUTH_CHANGE_PASSWORD = 1
    AUTH_LOCKED = 2

    def __init__(self):
        self._enabled = 0
        self._host = ''
        self._base_dn = ''
        self._domain = ''
        self._bind_user = ''
        self._bind_pass = ''
        self._mapping_username = ''
        self._mapping_fullname = ''
        self._mapping_email = ''
        self._ssl = 0

        # Internal.
        self.__error_message = ''
        self.__error_details = ''
        self.__last_result = None

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
    def mapping_fullname(self):
        return self._mapping_fullname

    @mapping_fullname.setter
    def mapping_fullname(self, value):
        self._mapping_fullname = value

    @property
    def mapping_email(self):
        return self._mapping_email

    @mapping_email.setter
    def mapping_email(self, value):
        self._mapping_email = value

    @property
    def error_message(self):
        return self.__error_message

    @error_message.setter
    def error_message(self, value):
        self.__error_message = value

    @property
    def error_details(self):
        return self.__error_details

    @error_details.setter
    def error_details(self, value):
        self.__error_details = value

    @property
    def last_result(self):
        return self.__last_result

    @last_result.setter
    def last_result(self, value):
        self.__last_result = value

    def is_enabled(self):
        return self._enabled > 0

    def authenticate(self, username, password):
        connection = self.__connect(username, password)
        if connection:
            # Authentication worked - close connection.
            connection.unbind()

            # Reconnect using the BindUser and return the user's data.
            return {'result': self.AUTH_SUCCESS, 'user': self.__load_user(username)}
        return self.__process_result(self.last_result)

    def __load_user(self, username):
        connection = self.__connect(self.bind_user, self.bind_pass)
        if not connection:
            return False

        # Get the mandatory fields first.
        attributes = [self.mapping_username, self.mapping_fullname]

        # Now the optional fields.
        if len(self.mapping_email) > 0:
            attributes.append(self.mapping_email)

        search = "(&(objectclass=person)({0}={1}))".format(self.mapping_username, username)
        connection.search(self.base_dn, search, attributes=attributes)
        if len(connection.entries) != 1:
            # We're only looking for one record - anything else is an error and it shouldn't have reached this point.
            connection.unbind()
            return False

        response = connection.response[0]
        response_attributes = response['attributes']

        data = {
            'username': response_attributes[self.mapping_username] if self.mapping_username in response_attributes else '',
            'fullname': response_attributes[self.mapping_fullname] if self.mapping_fullname in response_attributes else '',
            'email': response_attributes[self.mapping_email] if self.mapping_email in response_attributes else '',
            'dn': response['dn']
        }

        if isinstance(data['email'], list):
            data['email'] = data['email'][0] if len(data['email']) > 0 else ''

        # Close connection.
        connection.unbind()

        return data

    def __process_result(self, result):
        # https://ldapwiki.com/wiki/Common%20Active%20Directory%20Bind%20Errors
        # Weird way to get the AD response as it only returns a string rather than the code in a property. It could
        # be the ldap3 library or the way AD returns the code, but I can't can't fix either one soooo here it is!
        ldap_responses = {
            'data 532': self.AUTH_CHANGE_PASSWORD,  # ERROR_PASSWORD_EXPIRED
            'data 773': self.AUTH_CHANGE_PASSWORD, # ERROR_PASSWORD_MUST_CHANGE
            'data 533': self.AUTH_LOCKED, # ERROR_ACCOUNT_DISABLED
        }

        response = self.AUTH_INVALID_LOGIN
        if ('message' in result) and (len(result['message']) > 0):
            for seed, code in ldap_responses.items():
                if seed in result['message']:
                    response = code
                    break

        return {'result': response}

    def __connect(self, username, password):
        server = ldap3.Server(self.host, get_info=ldap3.ALL, use_ssl=self.ssl)
        ldap_user = "{0}\\{1}".format(self.domain, username)
        connection = ldap3.Connection(server, user=ldap_user, password=password, authentication=ldap3.NTLM)
        try:
            self.last_result = None
            result = connection.bind()
            self.last_result = connection.result
        except (LDAPSocketOpenError, LDAPSocketSendError) as e:
            # I kept these separately as these are when it can't connect to the server.
            self.error_message = 'Internal Error: Could not connect to the LDAP Server.'
            self.error_details = str(e)

            return False
        except Exception as e:
            self.error_message = 'Internal Error: Something is wrong with the LDAP Server.'
            self.error_details = str(e)

            return False
        return connection if result else False

    def update_password_ad(self, username, old_password, new_password):
        # First we need to check their existing password.
        result = self.authenticate(username, old_password)
        if result['result'] != self.AUTH_CHANGE_PASSWORD:
            return False

        user = self.__load_user(username)
        if not user or len(user['username']) == 0:
            return False

        connection = self.__connect(self.bind_user, self.bind_pass)
        result = ad_modify_password(connection, user['dn'], new_password, old_password)
        return result
