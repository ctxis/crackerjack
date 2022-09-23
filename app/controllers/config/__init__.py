from flask import Blueprint

bp = Blueprint('config', __name__, url_prefix='/config')


from . import index
from .system import general, hashcat, webpush, ldap, azure, users, password_complexity, shell_logs, message, device_profiles
from .account import profile, theme, logins, api
