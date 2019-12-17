from flask_login import current_user, login_required
from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.lib.base.provider import Provider
import json, pprint


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


@bp.route('/<int:session_id>/setup/hashes', methods=['GET'])
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


@bp.route('/<int:session_id>/setup/hashes/save', methods=['POST'])
@login_required
def setup_hashes_save(session_id):
    provider = Provider()
    sessions = provider.sessions()

    if not sessions.can_access(current_user, session_id):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    hashes = request.form['hashes'].strip()

    save_as = sessions.get_hashfile_path(current_user.id, session_id)

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

    return redirect(url_for('sessions.setup_hashcat', session_id=session_id))


@bp.route('/<int:session_id>/setup/hashcat', methods=['GET'])
@login_required
def setup_hashcat(session_id):
    provider = Provider()
    sessions = provider.sessions()
    hashcat = provider.hashcat()
    wordlists = provider.wordlists()
    rules = provider.rules()

    if not sessions.can_access(current_user, session_id):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    session = sessions.get(current_user.id, session_id)[0]

    supported_hashes = hashcat.get_supported_hashes()
    # We need to process the array in a way to make it easy for JSON usage.
    supported_hashes = hashcat.compact_hashes(supported_hashes)

    password_wordlists = wordlists.get_wordlists()
    hashcat_rules = rules.get_rules()

    used_wordlists = sessions.get_used_wordlists(session_id)

    return render_template(
        'sessions/setup_hashcat.html',
        session=session,
        hashes_json=json.dumps(supported_hashes),
        wordlists_json=json.dumps(password_wordlists),
        used_wordlists=used_wordlists,
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

    flash('All settings saved. You can now start the session.', 'success')
    return redirect(url_for('sessions.view', session_id=session_id))


@bp.route('/<int:session_id>/view', methods=['GET'])
@login_required
def view(session_id):
    provider = Provider()
    sessions = provider.sessions()
    hashcat = provider.hashcat()

    if not sessions.can_access(current_user, session_id):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    session = sessions.get(current_user.id, session_id)[0]

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

    action = request.form['action'].strip()
    result = sessions.hashcat_action(session_id, action)

    return redirect(url_for('sessions.view', session_id=session_id))


@bp.route('/<int:session_id>/download/cracked', methods=['GET'])
@login_required
def download_cracked(session_id):
    provider = Provider()
    sessions = provider.sessions()

    if not sessions.can_access(current_user, session_id):
        flash('Access Denied', 'error')
        return redirect(url_for('home.index'))

    return sessions.download_file(session_id, 'cracked')
