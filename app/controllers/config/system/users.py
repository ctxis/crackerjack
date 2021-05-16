from .. import bp
from flask_login import login_required
from flask import render_template, redirect, url_for, flash, request
from app.lib.base.provider import Provider
from app.lib.base.decorators import admin_required
from app.lib.models.user import UserModel


@bp.route('/users', methods=['GET'])
@login_required
@admin_required
def users():
    return render_template(
        'config/system/users/index.html',
        users=UserModel.query.filter().order_by(UserModel.id).all()
    )


@bp.route('/users/<int:user_id>/edit', methods=['GET'])
@login_required
@admin_required
def user_edit(user_id):
    user = None if user_id <= 0 else UserModel.query.filter(UserModel.id == user_id).first()

    return render_template(
        'config/system/users/edit.html',
        user=user
    )


@bp.route('/users/<int:user_id>/save', methods=['POST'])
@login_required
@admin_required
def user_save(user_id):
    username = request.form['username'].strip() if 'username' in request.form else ''
    password = request.form['password'].strip() if 'password' in request.form else ''
    full_name = request.form['full_name'].strip() if 'full_name' in request.form else ''
    email = request.form['email'].strip() if 'email' in request.form else ''
    admin = int(request.form.get('admin', 0))
    ldap = int(request.form.get('ldap', 0))
    active = int(request.form.get('active', 0))

    provider = Provider()
    users = provider.users()

    if not users.save(user_id, username, password, full_name, email, admin, ldap, active):
        flash(users.get_last_error(), 'error')
        return redirect(url_for('admin.user_edit', user_id=user_id))

    flash('User saved', 'success')
    return redirect(url_for('config.users'))


@bp.route('/users/logins', methods=['GET'])
@login_required
@admin_required
def user_logins():
    provider = Provider()
    users = provider.users()
    user_logins = users.get_user_logins(0)

    return render_template(
        'config/system/users/logins.html',
        logins=user_logins
    )
