from flask import Blueprint, request, abort
from app.lib.base.provider import Provider


bp = Blueprint('api', __name__)


@bp.route('/session/create', methods=['POST'])
def session_create():
    provider = Provider()
    api = provider.api()
    sessions = provider.sessions()

    user = api.auth_api()
    data = api.get_json()

    if 'name' not in data:
        return api.response(False, 'Name not found in request')

    session = api.create_session(user.id, data['name'])
    if not session:
        return api.response(False, 'Could not create session')

    session = sessions.get(user.id, session.id)
    session = api.prep_session_response(session[0])

    return api.response(True, '', session)


@bp.route('/session/<int:session_id>', methods=['GET'])
def session_get(session_id):
    provider = Provider()
    api = provider.api()
    sessions = provider.sessions()

    user = api.auth_api()

    if not sessions.can_access(user, session_id):
        abort(403)

    session = sessions.get(user.id, session_id)
    session = api.prep_session_response(session[0])

    return api.response(True, '', session)


@bp.route('/session/<int:session_id>/hashes', methods=['POST'])
def session_hashes(session_id):
    provider = Provider()
    api = provider.api()
    sessions = provider.sessions()

    user = api.auth_api()
    data = api.get_json()

    if not sessions.can_access(user, session_id):
        abort(403)

    if 'hashes' not in data:
        return api.response(False, 'Hashes not found in request')

    sessions.save_hashes(user.id, session_id, data['hashes'])

    return api.response(True)


@bp.route('/session/<int:session_id>/hashcat', methods=['POST'])
def session_hashcat(session_id):
    provider = Provider()
    api = provider.api()
    hashcat = provider.hashcat()
    sessions = provider.sessions()
    wordlists = provider.wordlists()
    rules = provider.rules()

    user = api.auth_api()
    data = api.get_json()

    if not sessions.can_access(user, session_id):
        abort(403)

    checks = {
        'hash_type': 'Hash Type not found',
        'mode': 'Mode not found',
        'mask': 'Mask not found',
        'increment_min': 'Increment Min not found',
        'increment_max': 'Increment Max not found',
        'wordlist': 'Wordlist not found',
        'rule': 'Rule not found',
        'enable_increments': 'Enable Increments not found',
    }

    for field, error in checks.items():
        if field not in data:
            return api.response(False, error)

    hash_type = data['hash_type']
    mode = int(data['mode'])
    mask = data['mode']
    increment_min = int(data['increment_min'])
    increment_max = int(data['increment_max'])
    wordlist = data['wordlist']
    rule = data['rule']
    enable_increments = int(data['enable_increments'])
    wordlist_location = ''
    rule_location = ''

    if not hashcat.is_valid_hash_type(hash_type):
        return api.response(False, 'Invalid Hash Type')
    elif mode != 0 and mode != 3:
        return api.response(False, 'Invalid Mode')
    elif mode == 0:
        if not wordlists.is_valid_wordlist(wordlist):
            return api.response(False, 'Invalid Wordlist')
        elif len(rule) > 0 and not rules.is_valid_rule(rule):
            return api.response(False, 'Invalid Rule')

        wordlist_location = wordlists.get_wordlist_path(wordlist)
        rule_location = rules.get_rule_path(rule)
    elif mode == 3:
        if enable_increments > 0:
            if increment_min <= 0:
                return api.response(False, 'Invalid Increment Minimum')
            elif increment_max <= 0:
                return api.response(False, 'Invalid Increment Maximum')
            elif increment_min > increment_max:
                return api.response(False, 'Increment Minimum cannot be bigger than Increment Maximum')

    sessions.set_hashcat_setting(session_id, 'mode', mode)
    sessions.set_hashcat_setting(session_id, 'hashtype', hash_type)
    sessions.set_hashcat_setting(session_id, 'wordlist', wordlist_location)
    sessions.set_hashcat_setting(session_id, 'rule', rule_location)
    sessions.set_hashcat_setting(session_id, 'mask', mask)
    sessions.set_hashcat_setting(session_id, 'increment_min', increment_min)
    sessions.set_hashcat_setting(session_id, 'increment_max', increment_max)

    session = sessions.get(user.id, session_id)
    session = api.prep_session_response(session[0])

    return api.response(True, '', session)


@bp.route('/wordlists', methods=['GET'])
def wordlists_get():
    provider = Provider()
    api = provider.api()
    wordlists = provider.wordlists()

    user = api.auth_api()

    all_wordlists = api.prep_wordlist_response(wordlists.get_wordlists())

    return api.response(True, '', all_wordlists)


@bp.route('/rules', methods=['GET'])
def rules_get():
    provider = Provider()
    api = provider.api()
    rules = provider.rules()

    user = api.auth_api()

    all_rules = api.prep_rule_response(rules.get_rules())

    return api.response(True, '', all_rules)


@bp.route('/hashtypes', methods=['GET'])
def hashtypes_get():
    provider = Provider()
    api = provider.api()
    hashcat = provider.hashcat()

    user = api.auth_api()

    types = hashcat.compact_hashes(hashcat.get_supported_hashes())

    return api.response(True, '', types)


@bp.route('/session/<int:session_id>/action', methods=['POST'])
def session_action(session_id):
    provider = Provider()
    api = provider.api()
    sessions = provider.sessions()

    user = api.auth_api()
    data = api.get_json()

    if not sessions.can_access(user, session_id):
        abort(403)

    if 'action' not in data:
        return api.response(False, 'Action not found in request')

    action = data['action']
    if not sessions.hashcat_action(session_id, action):
        return api.response(False, 'Could not execute action')

    return api.response(True)


@bp.route('/session/<int:session_id>/download/<string:which_file>', methods=['POST'])
def session_download(session_id, which_file):
    provider = Provider()
    api = provider.api()
    sessions = provider.sessions()

    user = api.auth_api()

    if not sessions.can_access(user, session_id):
        abort(403)

    return sessions.download_file(session_id, which_file)
