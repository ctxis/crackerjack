from flask import Blueprint
from flask_login import current_user, login_required
from flask import render_template, redirect, url_for, flash, request
from app.lib.base.provider import Provider
from werkzeug.utils import secure_filename
import pprint


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

    return redirect(url_for('sessions.setup_hashes', session_id=session.id))


@bp.route('/view/<int:session_id>/setup/hashes', methods=['GET'])
@login_required
def setup_hashes(session_id):
    provider = Provider()
    sessions = provider.sessions()

    if not sessions.can_access(current_user, session_id):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    session = sessions.get(current_user.id, session_id)[0]

    return render_template(
        'sessions/setup_hashes.html',
        session=session
    )


@bp.route('/view/<int:session_id>/setup/hashes/save', methods=['POST'])
@login_required
def setup_hashes_save(session_id):
    provider = Provider()
    sessions = provider.sessions()

    if not sessions.can_access(current_user, session_id):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    hashes = request.form['hashes'].strip()

    save_as = sessions.get_hashfile_path(current_user.id)

    if len(hashes) > 0:
        with open(save_as, 'w') as f:
            f.write(hashes)
    else:
        if len(request.files) != 1:
            flash('Uploaded file could not be found', 'error')
            return redirect(url_for('sessions.setup_hashes', session_id=session_id))

        file = request.files['hashfile']
        if file.filename == '':
            flash('No hashes uploaded', 'error')
            return redirect(url_for('sessions.setup_hashes', session_id=session_id))

        file.save(save_as)

    return 'save'