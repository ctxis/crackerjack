from flask import Blueprint
from flask_login import current_user, login_required
from flask import request
from app.lib.base.provider import Provider
import json


bp = Blueprint('webpush', __name__)


@bp.route('/register', methods=['POST'])
@login_required
def register():
    response = {'success': True, 'message': ''}

    provider = Provider()
    webpush = provider.webpush()

    user_endpoint = request.form['user_endpoint'].strip()
    user_key = request.form['user_key'].strip()
    user_authsecret = request.form['user_authsecret'].strip()

    subscription = webpush.register(current_user.id, user_endpoint, user_key, user_authsecret)
    if not subscription:
        response['sucess'] = False,
        response['message'] = 'Could not register your web push subscription'

    return json.dumps(response)
