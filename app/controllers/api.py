from flask import Blueprint, Response
from app.lib.api.sessions import ApiSession
from app.lib.api.hashes import ApiHashes
from app.lib.api.hashcat import ApiHashcat
from app.lib.api.wordlists import ApiWordlists
from app.lib.api.rules import ApiRules
from app.lib.api.mask import ApiMask
from app.lib.api.auth import ApiAuth
from app.lib.api.base import ApiBase
from flask_login import current_user


bp = Blueprint('api', __name__)


@bp.route('/swagger.yaml', methods=['GET'])
def swagger():
    base = ApiBase()
    data = base.get_swagger_file('v1')

    response = Response()
    response.headers.add('Content-Type', 'text/plain')
    response.data = data
    return response


@bp.route('/sessions', methods=['POST'])
def session_create():
    auth = ApiAuth()
    base = ApiBase()
    sessions = ApiSession()

    if not auth.auth(True):
        return base.send_access_denied_response()

    return sessions.create(current_user.id, current_user.username)


@bp.route('/sessions', methods=['GET'])
def session_get_all():
    auth = ApiAuth()
    base = ApiBase()
    sessions = ApiSession()

    if not auth.auth(True):
        return base.send_access_denied_response()

    return sessions.get_all(current_user.id)


@bp.route('/sessions/<int:session_id>', methods=['GET'])
def session_get(session_id):
    auth = ApiAuth()
    base = ApiBase()
    sessions = ApiSession()

    if not auth.auth(True):
        return base.send_access_denied_response()
    elif not sessions.can_access(current_user, session_id):
        return base.send_access_denied_response()

    return sessions.get(user_id=current_user.id, session_id=session_id)


@bp.route('/sessions/<int:session_id>/validate', methods=['GET'])
def session_validate(session_id):
    auth = ApiAuth()
    base = ApiBase()
    sessions = ApiSession()

    if not auth.auth(True):
        return base.send_access_denied_response()
    elif not sessions.can_access(current_user, session_id):
        return base.send_access_denied_response()

    return sessions.validate(current_user.id, session_id)


@bp.route('/sessions/<int:session_id>/state', methods=['GET'])
def session_state(session_id):
    auth = ApiAuth()
    base = ApiBase()
    sessions = ApiSession()

    if not auth.auth(True):
        return base.send_access_denied_response()
    elif not sessions.can_access(current_user, session_id):
        return base.send_access_denied_response()

    return sessions.state(current_user.id, session_id)


@bp.route('/sessions/<int:session_id>/termination', methods=['POST'])
def session_termination(session_id):
    auth = ApiAuth()
    base = ApiBase()
    sessions = ApiSession()

    if not auth.auth(True):
        return base.send_access_denied_response()
    elif not sessions.can_access(current_user, session_id):
        return base.send_access_denied_response()

    return sessions.termination(current_user.id, session_id)


@bp.route('/sessions/<int:session_id>/notifications', methods=['POST'])
def session_notifications(session_id):
    auth = ApiAuth()
    base = ApiBase()
    sessions = ApiSession()

    if not auth.auth(True):
        return base.send_access_denied_response()
    elif not sessions.can_access(current_user, session_id):
        return base.send_access_denied_response()

    return sessions.notifications(current_user.id, session_id)


@bp.route('/sessions/<int:session_id>/execute', methods=['POST'])
def session_action(session_id):
    auth = ApiAuth()
    base = ApiBase()
    sessions = ApiSession()

    if not auth.auth(True):
        return base.send_access_denied_response()
    elif not sessions.can_access(current_user, session_id):
        return base.send_access_denied_response()

    return sessions.action(current_user.id, session_id)


@bp.route('/hashes/<int:session_id>/upload', methods=['POST'])
def hashes_upload(session_id):
    auth = ApiAuth()
    base = ApiBase()
    sessions = ApiSession()
    hashes = ApiHashes()

    if not auth.auth(True):
        return base.send_access_denied_response()
    elif not sessions.can_access(current_user, session_id):
        return base.send_access_denied_response()

    return hashes.upload(current_user.id, session_id)


@bp.route('/hashes/remote', methods=['GET'])
def hashes_remote():
    auth = ApiAuth()
    base = ApiBase()
    hashes = ApiHashes()

    if not auth.auth(True):
        return base.send_access_denied_response()

    return hashes.get_remote()


@bp.route('/hashes/<int:session_id>/remote', methods=['POST'])
def hashes_remote_set(session_id):
    auth = ApiAuth()
    base = ApiBase()
    sessions = ApiSession()
    hashes = ApiHashes()

    if not auth.auth(True):
        return base.send_access_denied_response()
    elif not sessions.can_access(current_user, session_id):
        return base.send_access_denied_response()

    return hashes.set_remote(current_user.id, session_id)


@bp.route('/hashes/<int:session_id>/download', methods=['POST'])
def hashes_download(session_id):
    auth = ApiAuth()
    base = ApiBase()
    sessions = ApiSession()
    hashes = ApiHashes()

    if not auth.auth(True):
        return base.send_access_denied_response()
    elif not sessions.can_access(current_user, session_id):
        return base.send_access_denied_response()

    return hashes.download(current_user.id, session_id)


@bp.route('/hashcat/types', methods=['GET'])
def hashcat_types():
    auth = ApiAuth()
    base = ApiBase()
    hashcat = ApiHashcat()

    if not auth.auth(True):
        return base.send_access_denied_response()

    return hashcat.get_types()


@bp.route('/hashcat/<int:session_id>/type', methods=['POST'])
def hashcat_type_set(session_id):
    auth = ApiAuth()
    base = ApiBase()
    sessions = ApiSession()
    hashcat = ApiHashcat()

    if not auth.auth(True):
        return base.send_access_denied_response()
    elif not sessions.can_access(current_user, session_id):
        return base.send_access_denied_response()

    return hashcat.set_type(current_user.id, session_id)


@bp.route('/hashcat/<int:session_id>/optimise', methods=['POST'])
def hashcat_set_optimisation(session_id):
    auth = ApiAuth()
    base = ApiBase()
    sessions = ApiSession()
    hashcat = ApiHashcat()

    if not auth.auth(True):
        return base.send_access_denied_response()
    elif not sessions.can_access(current_user, session_id):
        return base.send_access_denied_response()

    return hashcat.set_optimisation(current_user.id, session_id)


@bp.route('/hashcat/<int:session_id>/mode', methods=['POST'])
def hashcat_set_mode(session_id):
    auth = ApiAuth()
    base = ApiBase()
    sessions = ApiSession()
    hashcat = ApiHashcat()

    if not auth.auth(True):
        return base.send_access_denied_response()
    elif not sessions.can_access(current_user, session_id):
        return base.send_access_denied_response()

    return hashcat.set_mode(current_user.id, session_id)


@bp.route('/mask/<int:session_id>', methods=['POST'])
def mask_set(session_id):
    auth = ApiAuth()
    base = ApiBase()
    sessions = ApiSession()
    mask = ApiMask()

    if not auth.auth(True):
        return base.send_access_denied_response()
    elif not sessions.can_access(current_user, session_id):
        return base.send_access_denied_response()

    return mask.set_mask(current_user.id, session_id)


@bp.route('/mask/<int:session_id>/increment', methods=['POST'])
def mask_increment_set(session_id):
    auth = ApiAuth()
    base = ApiBase()
    sessions = ApiSession()
    mask = ApiMask()

    if not auth.auth(True):
        return base.send_access_denied_response()
    elif not sessions.can_access(current_user, session_id):
        return base.send_access_denied_response()

    return mask.set_increment(current_user.id, session_id)


@bp.route('/wordlists', methods=['GET'])
def wordlists():
    auth = ApiAuth()
    base = ApiBase()
    wordlists = ApiWordlists()

    if not auth.auth(True):
        return base.send_access_denied_response()

    return wordlists.get()


@bp.route('/wordlists/<int:session_id>/type', methods=['POST'])
def wordlist_set_type(session_id):
    auth = ApiAuth()
    base = ApiBase()
    sessions = ApiSession()
    wordlists = ApiWordlists()

    if not auth.auth(True):
        return base.send_access_denied_response()
    elif not sessions.can_access(current_user, session_id):
        return base.send_access_denied_response()

    return wordlists.set_type(current_user.id, session_id)


@bp.route('/wordlists/<int:session_id>/global', methods=['POST'])
def wordlist_set_global(session_id):
    auth = ApiAuth()
    base = ApiBase()
    sessions = ApiSession()
    wordlists = ApiWordlists()

    if not auth.auth(True):
        return base.send_access_denied_response()
    elif not sessions.can_access(current_user, session_id):
        return base.send_access_denied_response()

    return wordlists.set_global(current_user.id, session_id)


@bp.route('/wordlists/<int:session_id>/custom', methods=['POST'])
def wordlist_set_custom(session_id):
    auth = ApiAuth()
    base = ApiBase()
    sessions = ApiSession()
    wordlists = ApiWordlists()

    if not auth.auth(True):
        return base.send_access_denied_response()
    elif not sessions.can_access(current_user, session_id):
        return base.send_access_denied_response()

    return wordlists.set_custom(current_user.id, session_id)


@bp.route('/wordlists/<int:session_id>/cracked', methods=['POST'])
def wordlist_set_cracked(session_id):
    auth = ApiAuth()
    base = ApiBase()
    sessions = ApiSession()
    wordlists = ApiWordlists()

    if not auth.auth(True):
        return base.send_access_denied_response()
    elif not sessions.can_access(current_user, session_id):
        return base.send_access_denied_response()

    return wordlists.set_cracked(current_user.id, session_id)


@bp.route('/rules', methods=['GET'])
def rules():
    auth = ApiAuth()
    base = ApiBase()
    rules = ApiRules()

    if not auth.auth(True):
        return base.send_access_denied_response()

    return rules.get()


@bp.route('/rules/<int:session_id>', methods=['POST'])
def rule_set(session_id):
    auth = ApiAuth()
    base = ApiBase()
    sessions = ApiSession()
    rules = ApiRules()

    if not auth.auth(True):
        return base.send_access_denied_response()
    elif not sessions.can_access(current_user, session_id):
        return base.send_access_denied_response()

    return rules.set(current_user.id, session_id)
