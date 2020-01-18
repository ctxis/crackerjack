from flask import Blueprint
from flask import render_template, redirect, url_for, flash, request
from app.lib.base.provider import Provider


bp = Blueprint('install', __name__)


@bp.route('/', methods=['GET'])
def index():
    provider = Provider()
    users = provider.users()

    if users.get_user_count() > 0:
        flash('Application has already been configured.', 'error')
        return redirect(url_for('home.index'))

    return render_template(
        'install/index.html'
    )


@bp.route('/save', methods=['POST'])
def save():
    provider = Provider()
    users = provider.users()

    if users.get_user_count() > 0:
        flash('Application has already been configured.', 'error')
        return redirect(url_for('home.index'))

    username = request.form['username'].strip()
    password = request.form['password'].strip()
    full_name = request.form['full_name'].strip()
    email = request.form['email'].strip()

    if len(username) == 0 or len(password) == 0 or len(full_name) == 0 or len(email) == 0:
        flash('Please fill in all the fields', 'error')
        return redirect(url_for('install.index'))

    if not users.save(0, username, password, full_name, email, 1, 0, 1):
        flash('Could not create user - make sure the database file is writable', 'error')
        return redirect(url_for('install.index'))

    flash('Please login as the newly created administrator', 'success')
    return redirect(url_for('home.index'))