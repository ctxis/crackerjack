from flask import Blueprint
from flask_login import login_user, logout_user, current_user
from flask import render_template, redirect, url_for, flash, request, session
from app.lib.models.user import UserModel
from sqlalchemy import and_, func
from app.lib.base.provider import Provider
from werkzeug.urls import url_parse
import urllib
import time


bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))

    return render_template('auth/login.html', next=request.args.get('next', ''))


@bp.route('/login', methods=['POST'])
def login_process():
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))

    provider = Provider()
    ldap = provider.ldap()
    users = provider.users()
    settings = provider.settings()

    username = request.form['username']
    password = request.form['password']
    next = urllib.parse.unquote_plus(request.form['next'].strip())

    allow_logins = int(settings.get('allow_logins', 0))

    # First check if user is local. Local users take priority.
    user = UserModel.query.filter(and_(func.lower(UserModel.username) == func.lower(username), UserModel.ldap == 0)).first()
    if user:
        if not users.validate_password(user.password, password):
            flash('Invalid credentials', 'error')
            return redirect(url_for('auth.login', next=next))
    elif ldap.is_enabled() and allow_logins == 1:
        ldap_result = ldap.authenticate(username, password)
        if ldap_result['result'] == ldap.AUTH_SUCCESS:
            ldap_user = ldap_result['user']
        elif ldap_result['result'] == ldap.AUTH_CHANGE_PASSWORD:
            session['ldap_username'] = username
            session['ldap_time'] = int(time.time())
            flash('Your LDAP password has expired or needs changing', 'error')
            return redirect(url_for('auth.ldap_changepwd', next=next))
        elif ldap_result['result'] == ldap.AUTH_LOCKED:
            flash('Your AD account is disabled', 'error')
            return redirect(url_for('auth.login', next=next))
        else:
            if len(ldap.error_message) > 0:
                flash(ldap.error_message, 'error')
            else:
                flash('Invalid credentials', 'error')
            return redirect(url_for('auth.login', next=next))

        user = users.get_ldap_user(ldap_user['username'])
        if not user:
            # Create
            user = users.create_ldap_user(ldap_user['username'], ldap_user['fullname'], ldap_user['email'])
            if not user:
                flash('Could not create LDAP user', 'error')
                return redirect(url_for('auth.login', next=next))
    else:
        flash('Invalid credentials', 'error')
        return redirect(url_for('auth.login', next=next))

    # If we reach this point it means that our user exists. Check if the user is active.
    if user.active is False:
        flash('Your account has been disabled by the Administrator.', 'error')
        return redirect(url_for('auth.login', next=next))

    user = users.login_session(user)
    login_user(user)
    users.record_login(user.id)

    # On every login we get the hashcat version and the git hash version.
    system = provider.system()
    system.run_updates()

    if next and url_parse(next).netloc == '':
        return redirect(next)

    return redirect(url_for('home.index'))


@bp.route('/logout', methods=['GET'])
def logout():
    provider = Provider()
    users = provider.users()

    users.logout_session(current_user.id)
    logout_user()
    return redirect(url_for('auth.login'))


@bp.route('/ldap/password', methods=['GET'])
def ldap_changepwd():
    provider = Provider()
    users = provider.users()

    next = urllib.parse.unquote_plus(request.args.get('next', '').strip())
    username = session['ldap_username'] if 'ldap_username' in session else ''
    ldap_time = session['ldap_time'] if 'ldap_time' in session else 0

    if len(username) == 0:
        session.pop('ldap_username', None)
        session.pop('ldap_time', None)
        return redirect(url_for('auth.login', next=next))
    elif int(time.time()) > (ldap_time + 120):
        session.pop('ldap_username', None)
        session.pop('ldap_time', None)
        return redirect(url_for('auth.login', next=next))

    user = users.get_ldap_user(username)
    if not user:
        session.pop('ldap_username', None)
        session.pop('ldap_time', None)
        return redirect(url_for('auth.login', next=next))

    return render_template('auth/ldap_password.html', next=request.args.get('next', ''))


@bp.route('/ldap/password', methods=['POST'])
def ldap_changepwd_process():
    provider = Provider()
    users = provider.users()
    ldap = provider.ldap()

    next = urllib.parse.unquote_plus(request.args.get('next', '').strip())
    password = request.form['password'].strip()
    new_password = request.form['new_password'].strip()
    confirm_password = request.form['confirm_password'].strip()

    username = session['ldap_username'] if 'ldap_username' in session else ''
    ldap_time = session['ldap_time'] if 'ldap_time' in session else 0
    if len(username) == 0:
        session.pop('ldap_username', None)
        session.pop('ldap_time', None)
        return redirect(url_for('auth.login', next=next))
    elif int(time.time()) > (ldap_time + 120):
        session.pop('ldap_username', None)
        session.pop('ldap_time', None)
        return redirect(url_for('auth.login', next=next))

    user = users.get_ldap_user(username)
    if not user:
        session.pop('ldap_username', None)
        session.pop('ldap_time', None)
        return redirect(url_for('auth.login', next=next))

    if len(password) == 0:
        flash('Please enter your current password', 'error')
        return redirect(url_for('ldap_changepwd', next=next))
    elif len(new_password) == 0 or len(confirm_password) == 0:
        flash('Please enter your new password', 'error')
        return redirect(url_for('ldap_changepwd', next=next))
    elif new_password != confirm_password:
        flash('New passwords do not match', 'error')
        return redirect(url_for('ldap_changepwd', next=next))

    session.pop('ldap_username', None)
    session.pop('ldap_time', None)

    if not ldap.update_password_ad(user.username, password, new_password):
        flash('Could not update password', 'error')
        return redirect(url_for('auth.login', next=next))

    flash('Password updated - please login again', 'success')
    return redirect(url_for('auth.login', next=next))
