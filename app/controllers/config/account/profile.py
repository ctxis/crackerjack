from .. import bp
from flask import current_app
from flask_login import login_required, current_user
from flask import render_template, redirect, url_for, flash, request
from app.lib.base.provider import Provider


@bp.route('/profile', methods=['GET'])
@bp.route('/profile/<int:user_id>', methods=['GET'])
@login_required
def profile(user_id=None):
    if user_id is None:
        user_id = current_user.id
    elif user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('home.index'))

    provider = Provider()
    users = provider.users()

    user = users.get_by_id(user_id)

    return render_template(
        'config/account/profile.html',
        user=user
    )


@bp.route('/profile/<int:user_id>/save', methods=['POST'])
@login_required
def profile_save(user_id):
    if user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('home.index'))

    provider = Provider()
    users = provider.users()
    user = users.get_by_id(current_user.id)

    if not user.ldap:
        existing_password = request.form['existing_password'].strip()
        new_password = request.form['new_password'].strip()
        confirm_password = request.form['confirm_password'].strip()

        if len(existing_password) == 0:
            flash('Please enter your existing password', 'error')
            return redirect(url_for('config.profile', user_id=user_id))
        elif len(new_password) == 0:
            flash('Please enter your new password', 'error')
            return redirect(url_for('config.profile', user_id=user_id))
        elif len(confirm_password) == 0:
            flash('Please confirm your new password', 'error')
            return redirect(url_for('config.profile', user_id=user_id))
        elif new_password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('config.profile', user_id=user_id))
        elif not users.validate_user_password(user_id, existing_password):
            flash('Existing password is invalid', 'error')
            return redirect(url_for('config.profile', user_id=user_id))
        elif not users.password_complexity.meets_requirements(new_password):
            flash(
                'Password does not meet complexity requirements: ' + users.password_complexity.get_requirement_description(),
                'error')
            return redirect(url_for('config.profile', user_id=user_id))

        users.update_password(user_id, new_password)

    flash('Settings updated', 'success')
    return redirect(url_for('config.profile', user_id=user_id))
