from flask import Blueprint
from flask_login import login_user, logout_user, current_user
from flask import render_template, redirect, url_for, flash, request
from app.lib.models.user import UserModel
from sqlalchemy import and_
from app.lib.base.provider import Provider


bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))

    return render_template('auth/login.html')


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

    allow_logins = int(settings.get('allow_logins', 0))

    # First check if user is local. Local users take priority.
    user = UserModel.query.filter(and_(UserModel.username == username, UserModel.ldap == 0)).first()
    if user:
        if not users.validate_password(user.password, password):
            flash('Invalid credentials', 'error')
            return redirect(url_for('auth.login'))
    elif ldap.is_enabled() and allow_logins == 1:
        if not ldap.authenticate(username, password, True):
            flash('Invalid credentials', 'error')
            return redirect(url_for('auth.login'))
        user = UserModel.query.filter(and_(UserModel.username == username, UserModel.ldap == 1)).first()
    else:
        flash('Invalid credentials', 'error')
        return redirect(url_for('auth.login'))

    login_user(user)

    # On every login we get the hashcat version and the git hash version.
    system = provider.system()
    system.run_updates()

    return redirect(url_for('home.index'))


@bp.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('auth.login'))