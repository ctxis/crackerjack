from flask import Blueprint
from flask_login import current_user
from flask import render_template, redirect, url_for, flash, request
from app.lib.base.provider import Provider


bp = Blueprint('home', __name__)


@bp.route('/', methods=['GET'])
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    provider = Provider()
    healthcheck = provider.healthcheck()

    errors = healthcheck.run(provider)
    if len(errors) > 0:
        for error in errors:
            flash(error, 'error')

    return render_template('home/index.html')
