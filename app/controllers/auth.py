from flask import Blueprint
from flask_login import login_user, logout_user, current_user
from flask import render_template, redirect, url_for, flash, request
import flask_bcrypt as bcrypt
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

    username = request.form['username']
    password = request.form['password']

    # First check if user is local. Local users take priority.
    user = UserModel.query.filter(and_(UserModel.username == username, UserModel.ldap == 0)).first()
    if user is None or not bcrypt.check_password_hash(user.password, password):
        # Next, we check LDAP.
        if ldap.is_enabled():
            if ldap.authenticate(username, password):
                user = ldap.load_user(username)
            else:
                flash('Invalid credentials', 'error')
                return redirect(url_for('auth.login'))
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