from flask import Blueprint
from flask_login import current_user
from flask import render_template, redirect, url_for, flash, request


bp = Blueprint('home', __name__)


@bp.route('/', methods=['GET'])
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    return render_template('home/index.html')

