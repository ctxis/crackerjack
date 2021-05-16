from functools import wraps
from flask_login import current_user
from flask import redirect, url_for, flash


def admin_required(f):
    @wraps(f)
    def wrapped_view(**kwargs):
        if not current_user.admin:
            flash('Access Denied', 'error')
            return redirect(url_for('home.index'))

        return f(**kwargs)
    return wrapped_view
