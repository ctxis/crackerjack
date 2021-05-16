from .. import bp
from flask import current_app
from flask_login import login_required, current_user
from flask import render_template, redirect, url_for, flash, request
from app.lib.base.provider import Provider


@bp.route('/logins', methods=['GET'])
@login_required
def logins():
    provider = Provider()
    users = provider.users()
    user_logins = users.get_user_logins(current_user.id)

    return render_template(
        'config/account/logins.html',
        logins=user_logins
    )
