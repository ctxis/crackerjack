from flask_login import current_user, login_required
from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.lib.base.provider import Provider
import json


bp = Blueprint('sessions', __name__)


@bp.route('/create', methods=['POST'])
@login_required
def create():
    provider = Provider()
    sessions = provider.sessions()

    description = request.form['description'].strip()
    if len(description) == 0:
        flash('Please enter a session description', 'error')
        return redirect(url_for('home.index'))

    prefix = sessions.sanitise_name(current_user.username) + '_'
    name = sessions.generate_name(prefix=prefix, length=4)

    if sessions.exists(current_user.id, name):
        flash('You already have an active session with this name. Either delete or use that one instead.', 'error')
        return redirect(url_for('home.index'))

    session = sessions.create(current_user.id, name, description)
    if session is None:
        flash('Could not create session', 'error')
        return redirect(url_for('home.index'))

    return redirect(url_for('sessions.setup_hashes', session_id=session.id))


@bp.route('/<int:session_id>/setup/hashes', methods=['GET'])
@login_required
def setup_hashes(session_id):
    provider = Provider()
    sessions = provider.sessions()

    if not sessions.can_access(current_user, session_id):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    user_id = 0 if current_user.admin else current_user.id
    session = sessions.get(user_id, session_id)[0]

    return render_template(
        'sessions/setup_hashes.html',
        session=session
    )


@bp.route('/<int:session_id>/setup/hashes/save', methods=['POST'])
@login_required
def setup_hashes_save(session_id):
    provider = Provider()
    sessions = provider.sessions()

    if not sessions.can_access(current_user, session_id):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    hashes = request.form['hashes'].strip()

    save_as = sessions.session_filesystem.get_hashfile_path(current_user.id, session_id)

    if len(hashes) > 0:
        sessions.session_filesystem.save_hashes(current_user.id, session_id, hashes)
    else:
        if len(request.files) != 1:
            flash('Uploaded file could not be found', 'error')
            return redirect(url_for('sessions.setup_hashes', session_id=session_id))

        file = request.files['hashfile']
        if file.filename == '':
            flash('No hashes uploaded', 'error')
            return redirect(url_for('sessions.setup_hashes', session_id=session_id))

        file.save(save_as)

    return redirect(url_for('sessions.setup_hashcat', session_id=session_id))


@bp.route('/<int:session_id>/setup/hashcat', methods=['GET'])
@login_required
def setup_hashcat(session_id):
    provider = Provider()
    sessions = provider.sessions()
    hashcat = provider.hashcat()
    wordlists = provider.wordlists()
    rules = provider.rules()
    system = provider.system()

    if not sessions.can_access(current_user, session_id):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    user_id = 0 if current_user.admin else current_user.id
    session = sessions.get(user_id, session_id)[0]

    supported_hashes = hashcat.get_supported_hashes()
    # We need to process the array in a way to make it easy for JSON usage.
    supported_hashes = hashcat.compact_hashes(supported_hashes)
    if len(supported_hashes) == 0:
        home_directory = system.get_system_user_home_directory()
        flash('Could not get the supported hashes from hashcat', 'error')
        flash('If you have compiled hashcat from source, make sure %s/.hashcat directory exists and is writable' % home_directory, 'error')

    password_wordlists = wordlists.get_wordlists()
    hashcat_rules = rules.get_rules()

    return render_template(
        'sessions/setup_hashcat.html',
        session=session,
        hashes_json=json.dumps(supported_hashes),
        wordlists_json=json.dumps(password_wordlists),
        rules=hashcat_rules
    )


@bp.route('/<int:session_id>/setup/hashcat/save', methods=['POST'])
@login_required
def setup_hashcat_save(session_id):
    provider = Provider()
    sessions = provider.sessions()
    hashcat = provider.hashcat()
    wordlists = provider.wordlists()
    rules = provider.rules()

    if not sessions.can_access(current_user, session_id):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    hash_type = request.form['hash-type'].strip()
    wordlist = request.form['wordlist'].strip()
    rule = request.form['rule'].strip()
    mode = int(request.form['mode'].strip())
    mask = request.form['compiled-mask'].strip()
    enable_increments = int(request.form.get('enable_increments', 0))
    if enable_increments == 1:
        increment_min = int(request.form['increment-min'].strip())
        increment_max = int(request.form['increment-max'].strip())
    else:
        increment_min = 0
        increment_max = 0

    if mode != 0 and mode != 3:
        # As all the conditions below depend on the mode, if it's wrong return to the previous page immediately.
        flash('Invalid attack mode selected', 'error')
        return redirect(url_for('sessions.setup_hashcat', session_id=session_id))

    has_errors = False
    if not hashcat.is_valid_hash_type(hash_type):
        has_errors = True
        flash('Invalid hash type selected', 'error')

    if mode == 0:
        # Wordlist.
        if not wordlists.is_valid_wordlist(wordlist):
            has_errors = True
            flash('Invalid wordlist selected', 'error')

        if len(rule) > 0 and not rules.is_valid_rule(rule):
            has_errors = True
            flash('Invalid rule selected', 'error')
    elif mode == 3:
        # Mask.
        if len(mask) == 0:
            flash('No mask set', 'error')
            has_errors = True

        if enable_increments == 1:
            if increment_min <= 0:
                has_errors = True
                flash('Min Increment is invalid', 'error')

            if increment_max <= 0:
                has_errors = True
                flash('Max Increment is invalid', 'error')

            if increment_min > increment_max:
                has_errors = True
                flash('Min Increment cannot be bigger than Max Increment', 'error')

        else:
            increment_min = 0
            increment_max = 0

    if has_errors:
        return redirect(url_for('sessions.setup_hashcat', session_id=session_id))

    wordlist_location = wordlists.get_wordlist_path(wordlist)
    rule_location = rules.get_rule_path(rule)

    sessions.set_hashcat_setting(session_id, 'mode', mode)
    sessions.set_hashcat_setting(session_id, 'hashtype', hash_type)
    sessions.set_hashcat_setting(session_id, 'wordlist', wordlist_location)
    sessions.set_hashcat_setting(session_id, 'rule', rule_location)
    sessions.set_hashcat_setting(session_id, 'mask', mask)
    sessions.set_hashcat_setting(session_id, 'increment_min', increment_min)
    sessions.set_hashcat_setting(session_id, 'increment_max', increment_max)

    return redirect(url_for('sessions.settings', session_id=session_id))


@bp.route('/<int:session_id>/view', methods=['GET'])
@login_required
def view(session_id):
    provider = Provider()
    sessions = provider.sessions()
    hashcat = provider.hashcat()

    if not sessions.can_access(current_user, session_id):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    user_id = 0 if current_user.admin else current_user.id
    session = sessions.get(user_id, session_id)[0]

    supported_hashes = hashcat.get_supported_hashes()
    # We need to process the array in a way to make it easy for JSON usage.
    supported_hashes = hashcat.compact_hashes(supported_hashes)

    return render_template(
        'sessions/view.html',
        session=session,
        supported_hashes=supported_hashes
    )


@bp.route('/<int:session_id>/action', methods=['POST'])
@login_required
def action(session_id):
    provider = Provider()
    sessions = provider.sessions()

    if not sessions.can_access(current_user, session_id):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    user_id = 0 if current_user.admin else current_user.id
    session = sessions.get(user_id, session_id)[0]

    if len(session['validation']) > 0:
        flash('Please configure all required settings and try again.', 'error')
        return redirect(url_for('sessions.view', session_id=session_id))

    action = request.form['action'].strip()
    result = sessions.hashcat_action(session_id, action)
    if result is False:
        flash('Could not execute action. Please check that all settings have been configured and try again.', 'error')
        return redirect(url_for('sessions.view', session_id=session_id))

    flash('If the STATE is not updated instantly, try refreshing this page in about 20-30 seconds.', 'success')
    return redirect(url_for('sessions.view', session_id=session_id))


@bp.route('/<int:session_id>/download/<string:which_file>', methods=['GET'])
@login_required
def download_file(session_id, which_file):
    provider = Provider()
    sessions = provider.sessions()

    if not sessions.can_access(current_user, session_id):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    return sessions.download_file(session_id, which_file)


@bp.route('/<int:session_id>/settings', methods=['GET'])
@login_required
def settings(session_id):
    provider = Provider()
    sessions = provider.sessions()

    if not sessions.can_access(current_user, session_id):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    user_id = 0 if current_user.admin else current_user.id
    session = sessions.get(user_id, session_id)[0]

    return render_template(
        'sessions/settings.html',
        session=session
    )


@bp.route('/<int:session_id>/settings/save', methods=['POST'])
@login_required
def settings_save(session_id):
    provider = Provider()
    sessions = provider.sessions()

    if not sessions.can_access(current_user, session_id):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    termination_date = request.form['termination_date'].strip()
    termination_time = request.form['termination_time'].strip()

    if len(termination_date) == 0:
        flash('Please enter a termination date', 'error')
        return redirect(url_for('sessions.settings', session_id=session_id))

    if len(termination_time) == 0:
        # Default to 23:59.
        termination_time = '23:59'

    if not sessions.set_termination_datetime(session_id, termination_date, termination_time):
        flash('Invalid termination date/time entered', 'error')
        return redirect(url_for('sessions.settings', session_id=session_id))

    flash('Settings saved', 'success')
    return redirect(url_for('sessions.settings', session_id=session_id))


@bp.route('/<int:session_id>/history/apply/<int:history_id>', methods=['POST'])
@login_required
def history_apply(session_id, history_id):
    provider = Provider()
    sessions = provider.sessions()

    if not sessions.can_access(current_user, session_id):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))
    elif not sessions.can_access_history(current_user, session_id, history_id):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    if not sessions.restore_hashcat_history(session_id, history_id):
        flash('Could not apply historical settings to the current session', 'error')
    else:
        flash('Historical settings applied', 'success')

    return redirect(url_for('sessions.view', session_id=session_id))
