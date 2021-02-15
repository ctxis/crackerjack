from flask_login import current_user, login_required
from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.lib.base.provider import Provider
import json


bp = Blueprint('sessions', __name__)


# https://stackoverflow.com/questions/19574694/flask-hit-decorator-before-before-request-signal-fires
def dont_update_session(func):
    func._dont_update_session = True
    return func


@bp.route('/create', methods=['POST'])
@login_required
def create():
    provider = Provider()
    sessions = provider.sessions()

    description = request.form['description'].strip()
    if len(description) == 0:
        flash('Please enter a session description', 'error')
        return redirect(url_for('home.index'))

    session = sessions.create(current_user.id, description, current_user.username)
    if session is None:
        flash('Could not create session', 'error')
        return redirect(url_for('home.index'))

    return redirect(url_for('sessions.setup_hashes', session_id=session.id))


@bp.route('/<int:session_id>/setup/hashes', methods=['GET'])
@login_required
def setup_hashes(session_id):
    provider = Provider()
    sessions = provider.sessions()
    uploaded_hashes = provider.hashes()

    if not sessions.can_access(current_user, session_id):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    user_id = 0 if current_user.admin else current_user.id
    session = sessions.get(user_id=user_id, session_id=session_id)[0]

    uploaded_hashfiles = uploaded_hashes.get_uploaded_hashes()

    return render_template(
        'sessions/setup/hashes.html',
        session=session,
        uploaded_hashfiles_json=json.dumps(uploaded_hashfiles, indent=4, sort_keys=True, default=str),
    )


@bp.route('/<int:session_id>/setup/hashes/save', methods=['POST'])
@login_required
def setup_hashes_save(session_id):
    provider = Provider()
    sessions = provider.sessions()
    uploaded_hashes = provider.hashes()

    if not sessions.can_access(current_user, session_id):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    mode = int(request.form['mode'].strip())
    contains_usernames = int(request.form.get('contains_usernames', 0))
    save_as = sessions.session_filesystem.get_hashfile_path(current_user.id, session_id)

    if mode == 0:
        # Upload file.
        if len(request.files) != 1:
            flash('Uploaded file could not be found', 'error')
            return redirect(url_for('sessions.setup_hashes', session_id=session_id))

        file = request.files['hashfile']
        if file.filename == '':
            flash('No hashes uploaded', 'error')
            return redirect(url_for('sessions.setup_hashes', session_id=session_id))

        file.save(save_as)
    elif mode == 1:
        # Enter hashes manually.
        hashes = request.form['hashes'].strip()
        if len(hashes) > 0:
            sessions.session_filesystem.save_hashes(current_user.id, session_id, hashes)
        else:
            flash('No hashes entered', 'error')
            return redirect(url_for('sessions.setup_hashes', session_id=session_id))
    elif mode == 2:
        # Select already uploaded file.
        remotefile = request.form['remotefile'].strip()
        if not uploaded_hashes.is_valid_uploaded_hashfile(remotefile):
            flash('Invalid uploaded file selected', 'error')
            return redirect(url_for('sessions.setup_hashes', session_id=session_id))

        remotefile_location = uploaded_hashes.get_uploaded_hashes_path(remotefile)

        if not uploaded_hashes.copy_file(remotefile_location, save_as):
            flash('Could not copy file', 'error')
            return redirect(url_for('sessions.setup_hashes', session_id=session_id))
    else:
        flash('Invalid mode selected', 'error')
        return redirect(url_for('sessions.setup_hashes', session_id=session_id))

    sessions.set_hashcat_setting(session_id, 'contains_usernames', contains_usernames)

    return redirect(url_for('sessions.setup_hashcat', session_id=session_id))


@bp.route('/<int:session_id>/setup/hashcat', methods=['GET'])
@login_required
def setup_hashcat(session_id):
    provider = Provider()
    sessions = provider.sessions()
    hashcat = provider.hashcat()
    system = provider.system()

    if not sessions.can_access(current_user, session_id):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    user_id = 0 if current_user.admin else current_user.id
    session = sessions.get(user_id=user_id, session_id=session_id)[0]

    supported_hashes = hashcat.get_supported_hashes()
    # We need to process the array in a way to make it easy for JSON usage.
    supported_hashes = hashcat.compact_hashes(supported_hashes)
    if len(supported_hashes) == 0:
        home_directory = system.get_system_user_home_directory()
        flash('Could not get the supported hashes from hashcat', 'error')
        flash('If you have compiled hashcat from source, make sure %s/.hashcat directory exists and is writable' % home_directory, 'error')

    return render_template(
        'sessions/setup/hashcat.html',
        session=session,
        hashes_json=json.dumps(supported_hashes, indent=4, sort_keys=True, default=str),
        guess_hashtype=sessions.guess_hashtype(session.user_id, session.id, session.hashcat.contains_usernames)
    )


@bp.route('/<int:session_id>/setup/hashcat/save', methods=['POST'])
@login_required
def setup_hashcat_save(session_id):
    provider = Provider()
    sessions = provider.sessions()
    hashcat = provider.hashcat()

    if not sessions.can_access(current_user, session_id):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    hash_type = request.form['hash-type'].strip()
    optimised_kernel = int(request.form.get('optimised_kernel', 0))
    workload = int(request.form.get('workload', 2))
    mode = int(request.form['mode'].strip())

    if mode != 0 and mode != 3:
        # As all the conditions below depend on the mode, if it's wrong return to the previous page immediately.
        flash('Invalid attack mode selected', 'error')
        return redirect(url_for('sessions.setup_hashcat', session_id=session_id))
    elif workload not in [1, 2, 3, 4]:
        flash('Invalid workload selected', 'error')
        return redirect(url_for('sessions.setup_hashcat', session_id=session_id))

    has_errors = False
    if not hashcat.is_valid_hash_type(hash_type):
        has_errors = True
        flash('Invalid hash type selected', 'error')

    if has_errors:
        return redirect(url_for('sessions.setup_hashcat', session_id=session_id))

    sessions.set_hashcat_setting(session_id, 'mode', mode)
    sessions.set_hashcat_setting(session_id, 'hashtype', hash_type)
    sessions.set_hashcat_setting(session_id, 'optimised_kernel', optimised_kernel)
    sessions.set_hashcat_setting(session_id, 'workload', workload)

    redirect_to = 'wordlist' if mode == 0 else 'mask'

    return redirect(url_for('sessions.setup_' + redirect_to, session_id=session_id))


@bp.route('/<int:session_id>/setup/mask', methods=['GET'])
@login_required
def setup_mask(session_id):
    provider = Provider()
    sessions = provider.sessions()

    if not sessions.can_access(current_user, session_id):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    user_id = 0 if current_user.admin else current_user.id
    session = sessions.get(user_id=user_id, session_id=session_id)[0]

    return render_template(
        'sessions/setup/mask.html',
        session=session
    )


@bp.route('/<int:session_id>/setup/mask/save', methods=['POST'])
@login_required
def setup_mask_save(session_id):
    provider = Provider()
    sessions = provider.sessions()

    if not sessions.can_access(current_user, session_id):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    mask = request.form['compiled-mask'].strip()
    enable_increments = int(request.form.get('enable_increments', 0))
    if enable_increments == 1:
        increment_min = int(request.form['increment-min'].strip())
        increment_max = int(request.form['increment-max'].strip())
    else:
        increment_min = 0
        increment_max = 0

    has_errors = False
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
        return redirect(url_for('sessions.setup_mask', session_id=session_id))

    sessions.set_hashcat_setting(session_id, 'mask', mask)
    sessions.set_hashcat_setting(session_id, 'increment_min', increment_min)
    sessions.set_hashcat_setting(session_id, 'increment_max', increment_max)

    return redirect(url_for('sessions.settings', session_id=session_id))


@bp.route('/<int:session_id>/setup/wordlist', methods=['GET'])
@login_required
def setup_wordlist(session_id):
    provider = Provider()
    sessions = provider.sessions()
    wordlists = provider.wordlists()
    rules = provider.rules()

    if not sessions.can_access(current_user, session_id):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    user_id = 0 if current_user.admin else current_user.id
    session = sessions.get(user_id=user_id, session_id=session_id)[0]

    return render_template(
        'sessions/setup/wordlist.html',
        session=session,
        wordlists=wordlists.get_wordlists(),
        rules=rules.get_rules()
    )


@bp.route('/<int:session_id>/setup/wordlist/save', methods=['POST'])
@login_required
def setup_wordlist_save(session_id):
    provider = Provider()
    sessions = provider.sessions()
    wordlists = provider.wordlists()
    rules = provider.rules()

    if not sessions.can_access(current_user, session_id):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    wordlist_type = int(request.form['wordlist_type'].strip())

    if wordlist_type == 0:
        # Global wordlist.
        wordlist = request.form['wordlist'].strip()
        if not wordlists.is_valid_wordlist(wordlist):
            flash('Invalid wordlist selected', 'error')
            return redirect(url_for('sessions.setup_wordlist', session_id=session_id))

        wordlist_location = wordlists.get_wordlist_path(wordlist)
        sessions.set_hashcat_setting(session_id, 'wordlist', wordlist_location)
    elif wordlist_type == 1:
        # Custom wordlist.
        save_as = sessions.session_filesystem.get_custom_wordlist_path(current_user.id, session_id, prefix='custom_wordlist_', random=True)
        if len(request.files) != 1:
            flash('Uploaded file could not be found', 'error')
            return redirect(url_for('sessions.setup_wordlist', session_id=session_id))

        file = request.files['custom_wordlist']
        if file.filename == '':
            flash('No hashes uploaded', 'error')
            return redirect(url_for('sessions.setup_wordlist', session_id=session_id))

        file.save(save_as)
        sessions.set_hashcat_setting(session_id, 'wordlist', save_as)
    elif wordlist_type == 2:
        # Create wordlist from cracked passwords.
        save_as = sessions.session_filesystem.get_custom_wordlist_path(current_user.id, session_id, prefix='pwd_wordlist')
        sessions.export_cracked_passwords(session_id, save_as)
        sessions.set_hashcat_setting(session_id, 'wordlist', save_as)
    else:
        flash('Invalid wordlist option', 'error')
        return redirect(url_for('sessions.setup_wordlist', session_id=session_id))

    sessions.set_hashcat_setting(session_id, 'wordlist_type', wordlist_type)

    rule = request.form['rule'].strip()
    if len(rule) > 0 and not rules.is_valid_rule(rule):
        flash('Invalid rule selected', 'error')
        return redirect(url_for('sessions.setup_wordlist', session_id=session_id))

    rule_location = rules.get_rule_path(rule)
    sessions.set_hashcat_setting(session_id, 'rule', rule_location)

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
    session = sessions.get(user_id=user_id, session_id=session_id)[0]

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
    session = sessions.get(user_id=user_id, session_id=session_id)[0]

    if len(session.validation) > 0:
        flash('Please configure all required settings and try again.', 'error')
        return redirect(url_for('sessions.view', session_id=session_id))

    action = request.form['action'].strip()
    result = sessions.hashcat_action(session_id, action)
    if result is False:
        flash('Could not execute action. Please check that all settings have been configured and try again.', 'error')
        return redirect(url_for('sessions.view', session_id=session_id))

    return redirect(url_for('sessions.view', session_id=session_id))


@bp.route('/<int:session_id>/download/<string:which_file>', methods=['POST'])
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
    session = sessions.get(user_id=user_id, session_id=session_id)[0]

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
    notifications_enabled = int(request.form.get('notifications_enabled', 0))

    if len(termination_date) == 0:
        flash('Please enter a termination date', 'error')
        return redirect(url_for('sessions.settings', session_id=session_id))

    if len(termination_time) == 0:
        # Default to 23:59.
        termination_time = '23:59'

    if not sessions.set_termination_datetime(session_id, termination_date, termination_time):
        flash('Invalid termination date/time entered', 'error')
        return redirect(url_for('sessions.settings', session_id=session_id))

    sessions.set_notifications(session_id, notifications_enabled)

    flash('Settings saved', 'success')
    return redirect(url_for('sessions.view', session_id=session_id))


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


@bp.route('/<int:session_id>/status', methods=['GET'])
@dont_update_session
@login_required
def status(session_id):
    provider = Provider()
    sessions = provider.sessions()

    response = {'success': False, 'status': -1}

    if not sessions.can_access(current_user, session_id):
        flash('Access Denied', 'error')
        return json.dumps(response)

    user_id = 0 if current_user.admin else current_user.id
    session = sessions.get(user_id=user_id, session_id=session_id)[0]

    return json.dumps({'result': True, 'status': session.hashcat.state})


@bp.route('/<int:session_id>/files', methods=['GET'])
@login_required
def files(session_id):
    provider = Provider()
    sessions = provider.sessions()

    if not sessions.can_access(current_user, session_id):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    user_id = 0 if current_user.admin else current_user.id
    session = sessions.get(user_id=user_id, session_id=session_id)[0]
    files = sessions.get_data_files(session.user_id, session_id)

    return render_template(
        'sessions/files.html',
        session=session,
        files=files
    )


@bp.route('/<int:session_id>/active/<string:action>', methods=['POST'])
@login_required
def active_action(session_id, action):
    provider = Provider()
    sessions = provider.sessions()

    if not sessions.can_access(current_user, session_id):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    if action not in ['show', 'hide']:
        flash('Invalid Action', 'error')
        return redirect(url_for('home.index'))

    active = True if action == 'show' else False
    sessions.set_active(session_id, active)

    flash('Session updated', 'success')
    return redirect(url_for('home.index'))


@bp.route('/<int:session_id>/delete', methods=['POST'])
@login_required
def delete(session_id):
    provider = Provider()
    sessions = provider.sessions()

    if not sessions.can_access(current_user, session_id):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    if not sessions.delete(session_id):
        flash('Could not delete session', 'error')
        return redirect(url_for('home.index'))

    flash('Session deleted', 'success')
    return redirect(url_for('home.index'))


@bp.route('/<int:session_id>/browse', methods=['GET'])
@login_required
def browse(session_id):
    provider = Provider()
    sessions = provider.sessions()

    if not sessions.can_access(current_user, session_id):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    user_id = 0 if current_user.admin else current_user.id
    session = sessions.get(user_id=user_id, session_id=session_id)[0]
    if not session.hashcat.contains_usernames:
        return redirect(url_for('sessions.view', session_id=session_id))
    cracked = sessions.get_cracked_passwords(session_id).split("\n")

    return render_template(
        'sessions/browse.html',
        session=session,
        cracked=json.dumps(cracked, indent=4, sort_keys=True, default=str)
    )
