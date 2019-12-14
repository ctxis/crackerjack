from flask import Blueprint
from flask_login import current_user, login_required
from flask import render_template, redirect, url_for, flash, request
from app.lib.base.provider import Provider


bp = Blueprint('sessions', __name__)


@bp.route('/create', methods=['POST'])
@login_required
def create():
    provider = Provider()
    sessions = provider.sessions()

    name = request.form['name'].strip()
    name = sessions.sanitise_name(name)
    if len(name) == 0:
        # Either the name contained only invalid characters, or no name was supplied.
        name = sessions.generate_name()

    if sessions.exists(current_user.id, name):
        flash('You already have an active session with this name. Either delete or use that one instead.', 'error')
        return redirect(url_for('home.index'))

    session = sessions.create(current_user.id, name)
    if session is None:
        flash('Could not create session', 'error')
        return redirect(url_for('home.index'))

    return redirect(url_for('sessions.setup', session_id=session.id))


@bp.route('/view/<int:session_id>/setup', methods=['GET'])
@login_required
def setup(session_id):
    return 'setup'