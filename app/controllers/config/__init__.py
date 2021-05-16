from flask import Blueprint

bp = Blueprint('config', __name__, url_prefix='/config')


from . import index
from .system import general, hashcat, webpush, ldap, users, password_complexity, shell_logs, message
from .account import profile, theme, logins, api
